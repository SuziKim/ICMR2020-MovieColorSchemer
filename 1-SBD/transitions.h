#if !defined TRANSITIONS_H
#define TRANSITIONS_H

#include <vector>
#include <istream>

struct transition {
	double _beg, _end;

	enum tran_t { abrupt, gradual };

	transition(double beg = 0.0, double end = 0.0) : _beg(beg), _end(end) {}

	tran_t type() const {
		if (_beg == _end)
			return abrupt;
		else
			return gradual;
	}

	friend std::ostream& operator<< (std::ostream& os, const transition& d);
	friend std::istream& operator>> (std::istream& is, transition& t);
};

using transitions = std::vector<transition>;

#endif // TRANSITIONS_H