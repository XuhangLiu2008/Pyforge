#include <pybind11/pybind11.h>

namespace py = pybind11;

struct Node {         // << move this up here
    int value;
    Node* prev;
    Node* next;
};

static const int POOL_SIZE = 1024;
static Node node_pool[POOL_SIZE];
static bool node_used[POOL_SIZE] = {false};

static Node* alloc_node(int v) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (!node_used[i]) {
            node_used[i] = true;
            node_pool[i].value = v;
            node_pool[i].prev = nullptr;
            node_pool[i].next = nullptr;
            return &node_pool[i];
        }
    }
    return nullptr; // pool full
}

static void free_node(Node* n) {
    int idx = n - node_pool;
    if (idx >= 0 && idx < POOL_SIZE) {
        node_used[idx] = false;
    }
}

struct DoublyList {
    Node* head;
    Node* tail;

    struct iterator {
        Node* current;

        iterator(Node* n) : current(n) {}

        int& operator*() const { return current->value; }

        iterator& operator++() {           // pre-increment
            if (current) current = current->next;
            return *this;
        }

        bool operator==(const iterator& other) const {
            return current == other.current;
        }

        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    iterator begin() { return iterator(head); }
    iterator end()   { return iterator(nullptr); }

    DoublyList(int v) {
        Node* n = alloc_node(v);
        head = tail = n;
    }

    void append(int v) {
        Node* n = alloc_node(v);
        n->prev = tail;
        tail->next = n;
        tail = n;
    }

    void prepend(int v) {
        Node* n = alloc_node(v);
        n->next = head;
        head->prev = n;
        head = n;
    }

    void remove(Node* node) {
        if (node->prev) node->prev->next = node->next;
        else head = node->next;

        if (node->next) node->next->prev = node->prev;
        else tail = node->prev;

        free_node(node);
    }

    int sum_forward() const {
        int s = 0;
        Node* cur = head;
        while (cur) {
            s += cur->value;
            cur = cur->next;
        }
        return s;
    }

    int sum_backward() const {
        int s = 0;
        Node* cur = tail;
        while (cur) {
            s += cur->value;
            cur = cur->prev;
        }
        return s;
    }
};

PYBIND11_MODULE(pcbridge, m) {
    py::class_<Node>(m, "Node")
        .def_readonly("value", &Node::value)
        .def_readonly("prev", &Node::prev)
        .def_readonly("next", &Node::next);

    py::class_<DoublyList>(m, "DoublyList")
        .def(py::init<int>())
        .def("append", &DoublyList::append)
        .def("prepend", &DoublyList::prepend)
        .def("remove", &DoublyList::remove)
        .def("sum_forward", &DoublyList::sum_forward)
        .def("sum_backward", &DoublyList::sum_backward)
        .def_readonly("head", &DoublyList::head)
        .def_readonly("tail", &DoublyList::tail)
        .def("__iter__", [](DoublyList &self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>());  // keep list alive while iterating
}