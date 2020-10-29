#include "differences.h"

#include "infix_iterator.h"

using namespace std;

ostream& operator<< (ostream& os, const diff& d) {
	os << d._frame << "\t";
	copy(d._differences.begin(), d._differences.end(), infix_ostream_iterator<double>(os, "\t"));
	return os;
}

istream& operator>> (istream& is, diff& d) {
	string line;
	if (!getline(is, line))
		return is;

	stringstream ss(line);
	if (!(ss >> d._frame)) {
		is.setstate(ios::failbit);
		return is;
	}

	double x;
	d._differences.clear();
	while (ss >> x) {
		d._differences.push_back(x);
	}
	return is;
}
