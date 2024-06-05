class KDNode:
    """
    A KDNode
    """
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right


class KDTree:
    """
    A KDTree


    """
    def __init__(self, points=None):
        self.k = 2
        self.root = None
        if points:
            self.root = self._build_tree(points)

    def add_point(self, point):
        if self.root is None:
            # self.k = len(point)
            self.root = KDNode(point)
        else:
            self._add_point(point, self.root, depth=0)

    def _add_point(self, point, node, depth):
        axis = depth % self.k

        if point[axis] < node.point[axis]:
            if node.left is None:
                node.left = KDNode(point)
            else:
                self._add_point(point, node.left, depth + 1)
        else:
            if node.right is None:
                node.right = KDNode(point)
            else:
                self._add_point(point, node.right, depth + 1)

    def _build_tree(self, points, depth=0):
        if not points:
            return None

        axis = depth % self.k
        sorted_points = sorted(points, key=lambda x: x[axis])
        median = len(sorted_points) // 2

        return KDNode(
            sorted_points[median],
            self._build_tree(sorted_points[:median], depth + 1),
            self._build_tree(sorted_points[median + 1:], depth + 1),
        )

    def _query(self, point, node, depth=0, best=None):
        if node is None:
            return best

        current_best = best
        current_node = node

        axis = depth % self.k
        next_best = None
        next_branch = None

        if point[axis] < node.point[axis]:
            next_node = node.left
            opposite_node = node.right
        else:
            next_node = node.right
            opposite_node = node.left

        next_best = self._query(point, next_node, depth + 1, current_best)

        if self._distance(point, current_node.point) < self._distance(point, next_best):
            next_best = current_node.point

        if abs(point[axis] - node.point[axis]) < self._distance(point, next_best):
            opposite_best = self._query(
                point, opposite_node, depth + 1, next_best)
            if self._distance(point, opposite_best) < self._distance(point, next_best):
                next_best = opposite_best

        return next_best

    def query(self, point):
        if point is None:
            raise Exception('There is no nodes in the Graph')
        try:
            best = self.root.point
        except:
            raise Exception('Ports/Marnet network was not initiated, initiate using searoute.utils.from_nodes_edges_set function')
        return self._query(point, self.root, 0, best)

    def _distance(self, p1, p2):
        return sum((x - y) ** 2 for x, y in zip(p1, p2)) ** 0.5
