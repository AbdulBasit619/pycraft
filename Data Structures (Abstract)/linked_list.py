class Node:
    """Class to create and manage nodes"""

    def __init__(self, value=None):
        """Initialize node with a value and reference to the next node (if exists!)."""
        self.value = value
        self.next = None

    def get_value(self):
        """Get value of the current node."""
        return self.value

    def set_value(self, value):
        """Set value of the current node."""
        self.value = value

    def get_next_node(self):
        """Get value of the next node."""
        return self.next

    def set_next_node(self, next_node):
        """Set value of the next node."""
        self.next = next_node


class LinkedList:
    """Overall class to manage Linked-List ADT (Abstract Data Type)."""

    def __init__(self):
        """Initialize a Linked List data structure."""
        self.head = Node(None)
        self.size = 0

    def _ensure_node(self, value):
        """Return a Node instance for the given value (no operation for Node input)."""
        return value if isinstance(value, Node) else Node(value)

    def add(self, node):
        """Add a node or value to the end of a Linked List."""

        # allow passing Node or value
        node = self._ensure_node(node)

        if self.head.get_value() is None:
            self.head = node
        else:
            current = self.head
            while current.get_next_node():
                current = current.get_next_node()
            current.set_next_node(node)
        self.size += 1

    def remove(self, value):
        """Delete a node from a Linked List."""
        current = self.head
        prev = None

        # allow passing Node or value
        value = self._ensure_node(value)

        while current:
            if current.get_value() == value.get_value():
                if prev:
                    prev.set_next_node(current.get_next_node())
                else:
                    self.head = current.get_next_node()
                self.size -= 1
                return True
            prev = current
            current = current.get_next_node()

        return False

    def find(self, value):
        """Find a node in the Linked List. Returns True if found, otherwise False."""
        current = self.head

        # allow passing Node or value
        value = self._ensure_node(value)

        while current:
            if current.get_value() == value.get_value():
                return True
            current = current.get_next_node()
        return False

    def get_size(self):
        """Return how many nodes does a Linked List object have."""
        return self.size

    def print_list(self):
        """Print all the elements in the Linked List."""
        if self.head is None:
            print("The list is empty!")
            return
        current = self.head
        while current:
            print(current.get_value(), end="")
            current = current.get_next_node()
            if current:
                print(" -> ", end="")
        print()


## Example Usage

# Create a linked list
linked_list = LinkedList()

# Add nodes
for i in range(0, 50, 5):
    linked_list.add(Node(i))

# Print linked list
linked_list.print_list()

# Find a node
value_to_find = 30
found_node = linked_list.find(value_to_find)
if found_node:
    print(f"Node with value {value_to_find} found!")
else:
    print(f"Node with value {value_to_find} not found.")

print("\n")
linked_list.print_list()

# Remove a node
value_to_remove = 30
if linked_list.remove(value_to_remove):
    print(f"Node with value {value_to_remove} removed.")
else:
    print(f"Node with value {value_to_remove} not found.")

print("\n")
linked_list.print_list()

print("\nSize of list:")
print(linked_list.get_size())
