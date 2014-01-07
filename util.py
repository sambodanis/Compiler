__author__ = 'sambodanis'


class Node:
    def __init__(self, data, next):
        self.data = data
        self.next = next

    def __str__(self):
        print self.data


class Stack:
    def __init__(self):
        self.top = None
        self.count = 0

    def __str__(self):
        c = self.top
        res = []
        while True:
            if c is None:
                break
            res.append(c.data)
            c = c.next
        return '[' + ', '.join(res) + ']'

    def push(self, item):
        if self.top is None:
            self.top = Node(item, None)
        else:
            new = Node(item, self.top)
            self.top = new
        self.count += 1

    def pop(self):
        if self.top is not None:
            result = self.top.data
            self.top = self.top.next
            self.count -= 1
            return result
        else:
            return None

    def peek(self):
        if self.count == 0:
            return None
        return self.top.data

    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0


class Queue:
    def __init__(self):
        self.first = None
        self.last = None
        self.count = 0

    def enqueue(self, item):
        if self.first is None:
            self.last = Node(item, None)
            self.first = self.last
        else:
            self.last.next = Node(item, None)
            self.last = self.last.next
        self.count += 1

    def dequeue(self):
        if self.first is not None:
            result = self.first.data
            self.first = self.first.next
            self.count -= 1
            return result
        return None

    def peek(self):
        if self.count == 0:
            return None
        return self.first.data

    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0
