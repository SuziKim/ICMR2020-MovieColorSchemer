#if !defined DIFFERENCES_H
#define DIFFERENCES_H

#include <assert.h>
#include <sstream>
#include <vector>

struct diff {
	double _frame;
	std::vector<double> _differences;

	diff() : _frame(-1.0) {}
	diff(double frame, size_t W) : _frame(frame), _differences(2 * W, 0.0) {}

	const double& operator[] (double w) const {
		assert(2 * w == int(2 * w));
		assert(int(2 * w) - 1 < _differences.size());
		return _differences[int(2 * w) - 1];
	}
	double& operator[] (double w) {
		return const_cast<double&>(const_cast<const diff&>(*this)[w]);
	}

	friend std::ostream& operator<< (std::ostream& os, const diff& d);
	friend std::istream& operator>> (std::istream& is, diff& d);
};

#endif // DIFFERENCES_H