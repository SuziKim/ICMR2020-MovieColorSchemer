#include "transitions.h"

using namespace std;

ostream& operator<< (ostream& os, const transition& t) {
	os << t._beg << "\t" << t._end << "\n";
	return os;
}

std::istream& operator>> (std::istream& is, transition& t) {
	is >> t._beg >> t._end;
	return is;
}

