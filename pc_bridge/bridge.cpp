#include <pybind11/pybind11.h>
#include <string>
#include <sstream>
#include <stdexcept>
#include <cstdint>

namespace py = pybind11;

struct Node {
    int value;
    Node* prev = nullptr;
    Node* next = nullptr;
    
    Node(int v) : value(v) {}
};

struct DoublyList {
    Node* head = nullptr;
    Node* tail = nullptr;
    size_t size = 0;

    struct iterator {
        Node* current;
        iterator(Node* n) : current(n) {}
        int& operator*() const { return current->value; }
        iterator& operator++() { 
            if (current) current = current->next; 
            return *this; 
        }
        bool operator==(const iterator& other) const { return current == other.current; }
        bool operator!=(const iterator& other) const { return !(*this == other); }
    };

    iterator begin() { return iterator(head); }
    iterator end()   { return iterator(nullptr); }

    DoublyList() {}
    DoublyList(int v) { append(v); }

    ~DoublyList() { clear(); }

    void clear() {
        Node* current = head;
        while (current) {
            Node* next = current->next;
            delete current;
            current = next;
        }
        head = tail = nullptr;
        size = 0;
    }

    void append(int v) {
        Node* n = new Node(v);
        if (!tail) {
            head = tail = n;
        } else {
            n->prev = tail;
            tail->next = n;
            tail = n;
        }
        size++;
    }

    void prepend(int v) {
        Node* n = new Node(v);
        if (!head) {
            head = tail = n;
        } else {
            n->next = head;
            head->prev = n;
            head = n;
        }
        size++;
    }

    void insert(int index, int v) {
        if (index < 0) index += (int)size;
        if (index < 0 || index > (int)size) {
            throw py::index_error();
        }

        if (index == 0) {
            prepend(v);
        } else if (index == (int)size) {
            append(v);
        } else {
            Node* current = get_node_at(index);
            Node* n = new Node(v);
            n->prev = current->prev;
            n->next = current;
            current->prev->next = n;
            current->prev = n;
            size++;
        }
    }

    // Remove a specific node. 
    // Note: This is unsafe if the node does not belong to this list or is already deleted.
    void remove_node(Node* node) {
        if (!node) return;

        if (node->prev) node->prev->next = node->next;
        else head = node->next;

        if (node->next) node->next->prev = node->prev;
        else tail = node->prev;

        delete node;
        size--;
    }

    void remove_value(int value) {
        Node* cur = head;
        while (cur) {
            if (cur->value == value) {
                remove_node(cur);
                return;
            }
            cur = cur->next;
        }
        throw std::invalid_argument("DoublyList.remove(x): x not in list");
    }

    // Deep
    uintptr_t get_memory_address() const {
        return reinterpret_cast<uintptr_t>(head);
    }

    uintptr_t get_node_memory_address(int index) const {
        Node* node = get_node_at(index);
        return reinterpret_cast<uintptr_t>(node);
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
    
    // Helper for indexing
    Node* get_node_at(int index) const {
        if (index < 0) index += (int)size;
        if (index < 0 || index >= (int)size) {
            throw py::index_error();
        }
        
        Node* cur;
        if (index < (int)size / 2) {
            cur = head;
            for (int i = 0; i < index; i++) cur = cur->next;
        } else {
            cur = tail;
            for (int i = 0; i < (int)size - 1 - index; i++) cur = cur->prev;
        }
        return cur;
    }
};

// Three global DoublyList instances
static DoublyList list1;
static DoublyList list2;
static DoublyList list3;

PYBIND11_MODULE(pcbridge, m) {
    py::class_<Node>(m, "Node")
        .def_readwrite("value", &Node::value)
        .def_readonly("prev", &Node::prev)
        .def_readonly("next", &Node::next)
        .def("__repr__", [](const Node& n) {
            return "<Node value=" + std::to_string(n.value) + ">";
        });

    py::class_<DoublyList>(m, "DoublyList")
        .def(py::init<>())
        .def(py::init<int>())
        .def("append", &DoublyList::append)
        .def("prepend", &DoublyList::prepend)
        .def("insert", &DoublyList::insert)
        .def("remove_node", &DoublyList::remove_node)
        .def("remove", &DoublyList::remove_value)
        .def("clear", &DoublyList::clear)
        .def("sum_forward", &DoublyList::sum_forward)
        .def("sum_backward", &DoublyList::sum_backward)
        .def("get_memory_address", &DoublyList::get_memory_address)
        .def("get_node_memory_address", &DoublyList::get_node_memory_address)
        .def_readonly("head", &DoublyList::head)
        .def_readonly("tail", &DoublyList::tail)
        .def_readonly("size", &DoublyList::size)
        
        // Python magic methods
        .def("__len__", [](const DoublyList& self) { return self.size; })
        .def("__getitem__", [](const DoublyList& self, int index) {
            return self.get_node_at(index)->value;
        })
        .def("__setitem__", [](DoublyList& self, int index, int value) {
            self.get_node_at(index)->value = value;
        })
        .def("__delitem__", [](DoublyList& self, int index) {
            const_cast<DoublyList&>(self).remove_node(self.get_node_at(index));
        })
        .def("__iter__", [](DoublyList &self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>())
        .def("__repr__", [](const DoublyList& self) {
            std::stringstream ss;
            ss << "DoublyList([";
            Node* cur = self.head;
            while (cur) {
                ss << cur->value;
                if (cur->next) ss << ", ";
                cur = cur->next;
            }
            ss << "])";
            return ss.str();
        });

    // Expose the three global instances to Python
    m.attr("list1") = &list1;
    m.attr("list2") = &list2;
    m.attr("list3") = &list3;
}