#pragma once
#include <Arduino.h>

template <typename T, size_t CAPACITY>
class Queue {
	public:
		bool isFull() {
			return _size == CAPACITY;
		}

		size_t size() {
			return _size;
		}

		/* Comportamento padrão:
		 * Se a fila estiver cheia, descarte o item mais antigo
		 */
		void push(const T& val) {
			if (isFull()) {
				T dummy;
				pop(dummy);
			}

			_tail = (_head + _size) % CAPACITY;
			_items[_tail] = val;
			_size++;
		}

		bool pop(T& out) {
			if (_size == 0) return false;

			out = _items[_tail];
			_head = (_head + 1) % CAPACITY;
			_size--;
			return true;
		}
		bool peek(T& out) {
			if (_size == 0) return false;
			out = _items[_tail];
			return true;
		}

		void clear() {
			_head = 0;
			_size = 0;
			_tail = 0;
		}
	private:
		T _items[CAPACITY];
		size_t _size = 0;
		size_t _head = 0;
		size_t _tail = 0;
};

