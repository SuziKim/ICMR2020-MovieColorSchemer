#if !defined THRESHOLDER_H
#define THRESHOLDER_H

#include "transitions.h"
#include "differences.h"

struct thresholder {
	const std::vector<diff>& _diffs;
	transitions _trans;

	thresholder(const std::vector<diff>& diffs) : _diffs(diffs) {}

	void apply(double w, double threshold, double threshold_time, double threshold_peak);
};

#endif // THRESHOLDER_H