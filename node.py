class Node:
    def __init__(self, value, depth, left_child=None, middle_child=None, right_child=None):
        self.value = value
        self.depth = depth
        self.left = left_child
        self.middle = middle_child
        self.right = right_child
