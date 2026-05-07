import networkx

_POSITION_KEY = "pos"

class GraphLocal:
    """
    Lightweight graph — loads .graphml and stores node positions in
    virtual screen-pixel space (same coordinate system as PC-side Graph).
    No pygame dependency.
    """

    def __init__(self, graph_file: str, scale_factor: float,
                 screen_height: int, flip_y: bool):
        self.scale_factor   = scale_factor
        self._screen_height = screen_height
        self._flip_y        = flip_y

        self.graph: networkx.DiGraph = networkx.read_graphml(graph_file)
        self.nodes: dict = {}
        self._load_nodes()

    def _load_nodes(self):
        for node, data in self.graph.nodes(data=True):
            if 'x' in data and 'y' in data:
                x = float(data['x']) * self.scale_factor
                y = float(data['y']) * self.scale_factor
                if self._flip_y:
                    y = self._screen_height - y
                self.nodes[node] = {_POSITION_KEY: (x, y)}
