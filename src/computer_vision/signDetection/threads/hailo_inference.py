import cv2
import numpy as np
from hailo_platform import VDevice, InferVStreams, HEF, InputVStreamParams, OutputVStreamParams
from src.computer_vision.signDetection.threads.hailo_results import to_ultralytics_results

class HailoYOLO:
    
    INPUT_W = 512
    INPUT_H = 288

    def __init__(self, hef_path: str, conf_threshold: float = 0.5, iou_threshold: float = 0.45):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        self.names = {
                        0: 'parking', 1: 'roundabout', 2: 'parkingSpotRight', 3: 'priority',
                        4: 'pedestrian', 5: 'crosswalk', 6: 'crosswalkRoad', 7: 'stop',
                        8: 'stopLine', 9: 'highwayEntry', 10: 'highwayExit', 11: 'light',
                        12: 'lightRed', 13: 'lightYellow', 14: 'lightGreen', 15: 'lightRedYellow',
                        16: 'oneWay', 17: 'parkingSpotLeft'
                    }

        self.vdevice = VDevice()
        self.hef = HEF(hef_path)

        self.network_group = self.vdevice.configure(self.hef)[0]
        self.input_vstreams_params = InputVStreamParams.make(self.network_group)

        for info in self.hef.get_output_vstream_infos():
            qp = info.quant_info
            print(f"{info.name}: zp={qp.qp_zp}, scale={qp.qp_scale}")

        self.output_vstreams_params = OutputVStreamParams.make(self.network_group)

        self._input_name = self.hef.get_input_vstream_infos()[0].name

        # Aktivacija network grupe — mora biti pre inference-a
        self._activated_network_group = self.network_group.activate()
        self._activated_network_group.__enter__()

        self._pipeline = InferVStreams(
            self.network_group,
            self.input_vstreams_params,
            self.output_vstreams_params,
        )
        self._pipeline.__enter__()

        for info in self.hef.get_output_vstream_infos():
            qp = info.quant_info
            print(f"{info.name}: zp={qp.qp_zp}, scale={qp.qp_scale}, name_check={'cls' if '18' in info.name else 'bbox'}")
        
        for info in self.hef.get_output_vstream_infos():
            if '18' in info.name: # cls stream
                self.cls_zp = info.quant_info.qp_zp
                self.cls_scale = info.quant_info.qp_scale
            else: # bbox stream
                self.bbox_zp = info.quant_info.qp_zp
                self.bbox_scale = info.quant_info.qp_scale

    def __del__(self):
        try:
            self._pipeline.__exit__(None, None, None)
            self._activated_network_group.__exit__(None, None, None)
        except Exception:
            pass

    def __call__(self, frame: np.ndarray, **kwargs):
        orig_h, orig_w = frame.shape[:2]

        blob = cv2.resize(frame, (self.INPUT_W, self.INPUT_H))
        blob = cv2.cvtColor(blob, cv2.COLOR_BGR2RGB)
        blob = np.expand_dims(blob, axis=0)

        raw = self._pipeline.infer({self._input_name: blob})

        detections = self._post_process(raw, orig_w, orig_h)
        return to_ultralytics_results(detections, self.names)

    def _post_process(self, raw_results, orig_w, orig_h):
        cls_tensor  = None
        bbox_tensor = None
        for k, v in raw_results.items():
            arr = np.squeeze(np.array(v, dtype=np.float32), axis=(0, 1))
            if arr.shape[1] == 18:
                cls_tensor = arr
            elif arr.shape[1] == 64:
                bbox_tensor = arr

        if cls_tensor is None or bbox_tensor is None:
            return []

        #cls_logits = (cls_tensor.astype(np.float32) - 0.0) * 0.003921568  # dequant
        cls_logits = (cls_tensor - self.cls_zp) * self.cls_scale
        # Softmax po klasama
        e = np.exp(cls_logits - cls_logits.max(axis=1, keepdims=True))
        cls_scores = e / e.sum(axis=1, keepdims=True)

        # I koristi direktno max kao conf bez adjusted:
        confs = cls_scores.max(axis=1)
        
        # --- DODATO: Izvlačenje ID-jeva klasa pre filtriranja ---
        cls_ids = cls_scores.argmax(axis=1)

        print(f"Softmax confs - min:{confs.min():.4f} max:{confs.max():.4f} mean:{confs.mean():.4f}")
        print(f"Top 5 confs: {np.sort(confs)[::-1][:5]}")
        
        # --- IZMENA: Koristi tvoj threshold iz config-a umesto hardkodovanog 0.5 ---
        mask = confs >= self.conf_threshold  
        
        if not mask.any():
            return []

        # Sada će ovo raditi savršeno
        cls_ids  = cls_ids[mask]
        confs    = confs[mask]
        bbox_raw = bbox_tensor[mask]

        #bbox_dequant = (bbox_raw - 87.0) * 1.6639
        bbox_dequant = (bbox_raw - self.bbox_zp) * self.bbox_scale
        bbox_dequant = bbox_dequant.reshape(-1, 4, 16)
        e       = np.exp(bbox_dequant - bbox_dequant.max(axis=2, keepdims=True))
        softmax = e / e.sum(axis=2, keepdims=True)
        dist    = (softmax * np.arange(16, dtype=np.float32)).sum(axis=2)

        print(f"dist sample (first 5): {dist[:5]}")
        print(f"dist min/max: {dist.min():.2f} / {dist.max():.2f}")

        anchors   = self._make_anchors()
        anchors_f = anchors[mask]

        x1 = (anchors_f[:, 0] - dist[:, 0]) / self.INPUT_W * orig_w
        y1 = (anchors_f[:, 1] - dist[:, 1]) / self.INPUT_H * orig_h
        x2 = (anchors_f[:, 0] + dist[:, 2]) / self.INPUT_W * orig_w
        y2 = (anchors_f[:, 1] + dist[:, 3]) / self.INPUT_H * orig_h

        # Minimum size filter
        w_box = x2 - x1
        h_box = y2 - y1
        size_mask = (w_box >= 5) & (h_box >= 5)

        # Odmah posle računanja w_box i h_box, pre size_mask
        print(f"Box sizes - w: min={w_box.min():.1f} max={w_box.max():.1f}, h: min={h_box.min():.1f} max={h_box.max():.1f}")

        if not size_mask.any():
            return []

        boxes   = np.stack([x1, y1, x2, y2], axis=1)[size_mask]
        confs   = confs[size_mask]
        cls_ids = cls_ids[size_mask]

        keep = self._nms(boxes, confs)

        print(f"Detections after NMS: {len(keep)}")
        for i in keep:
            print(f"  cls={cls_ids[i]} ({self.names.get(int(cls_ids[i]),'?')}), conf={confs[i]:.3f}, box={boxes[i].astype(int)}")

        return [
            {"xyxy": boxes[i].tolist(), "conf": float(confs[i]), "cls_id": int(cls_ids[i])}
            for i in keep
        ]

    def _make_anchors(self):
        """Generiše anchor centre za YOLOv8 grид na 3 skale."""
        anchors = []
        for stride, (gh, gw) in [
            (8,  (self.INPUT_H // 8,  self.INPUT_W // 8)),   # 36×64  = 2304
            (16, (self.INPUT_H // 16, self.INPUT_W // 16)),  # 18×32  = 576
            (32, (self.INPUT_H // 32, self.INPUT_W // 32)),  # 9×16   = 144
        ]:
            for gy in range(gh):
                for gx in range(gw):
                    anchors.append([(gx + 0.5) * stride, (gy + 0.5) * stride])
        return np.array(anchors, dtype=np.float32)  # (3024, 2)

    def _nms(self, boxes, scores, iou_threshold=0.45):
        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]
        keep  = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
            iou   = inter / (areas[i] + areas[order[1:]] - inter)
            order = order[1:][iou < iou_threshold]
        return keep