from dataclasses import dataclass
from typing import Optional, Any


COMMENT_SYMBOL = '%'


@dataclass(eq=False)
class Node2D:
    """
    This object is hashable via eq=False and __hash__->id(self).
    """
    above: 'Node2D' = None
    left: 'Node2D' = None
    right: 'Node2D' = None
    below: 'Node2D' = None
    control: 'Node2D' = None #< For non-control nodes to update their control node.
    value: Optional[Any] = None

    def __hash__(self):
        return id(self)

    def id(self):
        return id(self)

    def info_row(self) -> str:
        message = ""
        node = self
        while node.left:
            node = node.left
        while node:
            message += f"({node.value})-"
            node = node.right
        message = message.rstrip("-")
        return message

    def info_col(self) -> str:
        message = ""
        node = self
        while node.above:
            node = node.above
        while node:
            message += f"({node.value})-"
            node = node.below
        message = message.rstrip("-")
        return message


class LinkedList2D:
    def __init__(self) -> None:
        self.head = Node2D(value=float('inf'))
        self.ncols = 0
        self._history = []
    
    def _parse_size_line(self, line: str) -> None:
        self.ncols = int(line)
        prev = self.head
        for _ in range(self.ncols):
            node = Node2D(value=0)
            prev.right = node
            node.left = prev
            prev = node

    def _parse_coordinate_line(self, line: str) -> None:
        tokens = line.split(',')
        columns = [int(subtoken) for subtoken in tokens[0].split(" ")]
        values = [subtoken.rstrip() for subtoken in tokens[1].split(" ")]
        if len(columns) != len(values):
            raise Exception('Mismatch of columns to values')
        left = None
        for i in range(len(columns)):
            col_num = columns[i]
            if col_num > self.ncols:
                raise Exception("Column number is greater than the number of columns.")
            col = columns[i]
            node = Node2D(value=values[i])
            control = self.head
            for _ in range(col_num):
                control = control.right
            control.value += 1
            node.control = control
            prev_node = control
            next_node = control.below
            while next_node != None:
                prev_node = next_node
                next_node = next_node.below
            prev_node.below = node
            node.above = prev_node
            node.left = left
            if left:
                left.right = node
            left = node

    def _unlink_horizontal(self, node) -> None:
        if node.left:
            node.left.right = node.right
        if node.right:
            node.right.left = node.left

    def _link_horizontal(self, node) -> None:
        if node.left:
            node.left.right = node
        if node.right:
            node.right.left = node

    def _unlink_vertical(self, node) -> None:
        if node.control:
            node.control.value -= 1
        if node.above:
            node.above.below = node.below
        if node.below:
            node.below.above = node.above

    def _link_vertical(self, node) -> None:
        if node.control:
            node.control.value += 1
        if node.above:
            node.above.below = node
        if node.below:
            node.below.above = node

    def _remove_row(self, node) -> None:
        self._unlink_vertical(node)
        left = node.left
        while left:
            self._unlink_vertical(left)
            left = left.left
        right = node.right
        while right:
            self._unlink_vertical(right)
            right = right.right
        
    def _restore_row(self, node) -> None:
        self._link_vertical(node)
        left = node.left
        while left:
            self._link_vertical(left)
            left = left.left
        right = node.right
        while right:
            self._link_vertical(right)
            right = right.right

    # ------------------------------------ #
    #            Public  Methods           #
    # ------------------------------------ #
    def restore(self) -> bool:
        if not self._history:
            return False
        column = self._history.pop()
        self._link_horizontal(column)
        self._link_vertical(column)
        below = column.below
        while below:
            self._restore_row(below)
            below = below.below
        return True

    def remove_column(self, column) -> bool:
        if column is self.head:
            return False
        self._unlink_horizontal(column)
        self._unlink_vertical(column)
        self._history.append(column)
        below = column.below
        while below:
            self._remove_row(below)
            below = below.below
        return True

    def get_min_column(self) -> Node2D:
        node = min_node = self.head
        while node != None:
            if node.value < min_node.value:
                min_node = node
            node = node.right
        return min_node

    def get_nodes_from_column(self, column: Node2D) -> [Node2D]:
        nodes = []
        below = column.below
        while below:
            nodes.append(below)
            below = below.below
        return nodes

    def get_columns_from_row(self, row: Node2D) -> [Node2D]:
        columns = []
        while row.left:
            row = row.left
        while row:
            above = row.above
            while above.above:
                above = above.above
            columns.append(above)
            row = row.right
        return columns

    def get_row_from_node(self, node: Node2D) ->[Node2D]:
        row = []
        left = node
        while left.left:
            left = left.left
        right = left
        while right:
            row.append(right)
            right = right.right
        return row

    def load(self, pathname: str) -> None:
        with open(pathname, 'r') as f:
            line = f.readline()
            while line.startswith('%'):
                line = f.readline()
            self._parse_size_line(line)
            for coordinate_line in f:
                self._parse_coordinate_line(coordinate_line)

    def info(self) -> str:
        message = ""
        min_col = self.get_min_column()
        width = 10
        col_num = 0
        col_node = self.head
        message += f"{'--'*(width+1)}\n"
        message += f"|{'col':^{width}}{'nnz':^{width}}|\n"
        while col_node:
            message += f"|{str(col_num) + ":":^{width}}"
            message += f"{("*" if col_node is min_col else "")+str(col_node.value):^{width}}:"
            row_node = col_node.below
            while row_node:
                message += f"{row_node.value:^{width}}->"
                row_node = row_node.below
            col_num += 1
            message = message.rstrip("->") + "\n"
            col_node = col_node.right
        if not self._history:
            message += f"{'--'*(width+1)}"
            return message
        message += "~~" * (width + 1) + "\n"
        message += f"|{"history":^{width*2}}|\n"
        for index, col_node in enumerate(self._history):
            message += f"|{str(index) + ":":^{width}}"
            message += f"{"(" + str(col_node.value) + ")":^{width}}:"
            row_node = col_node.below
            while row_node:
                message += f"{row_node.value:^{width}}->"
                row_node = row_node.below
            message = message.rstrip("->") + "\n"
        message += f"{'--'*(width+1)}"
        return message