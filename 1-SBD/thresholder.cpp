#include "thresholder.h"

#include <algorithm>

using namespace std;

void thresholder::apply(double w, double threshold, double threshold_time, double threshold_peak) {
	if (_trans.size() == 0) {
		for (const auto& frame : _diffs) {
			if (frame[0.5] > threshold) {
				_trans.emplace_back(frame._frame, frame._frame);
			}
		}

		// Transitions filtering: if is connected to the previous one, remove it
		for (size_t i = 1; i < _trans.size();) {
			if (_trans[i]._beg - _trans[i - 1]._end < 1) {
				_trans[i - 1]._end = _trans[i]._end;
				_trans.erase(_trans.begin() + i);
			}
			else
				i++;
		}

		// Transition validation
		for (size_t i = 0; i < _trans.size();) {
			// Maximum within the transition
			double max_inside = 0;
			for (double j = _trans[i]._beg * 2; j <= _trans[i]._end * 2; ++j) {
				if (max_inside < _diffs[int(j)][w])
					max_inside = _diffs[int(j)][w];
			}
			// Minimum outside the transition at distance 2*w+1 on both sides
			int before = max(0, int(_trans[i]._beg * 2 - (2 * w + 1)));
			int after = min(int(_trans[i]._end * 2 + (2 * w + 1)), int(_diffs.size() - 1));
			double min_outside = min(_diffs[before][w], _diffs[after][w]);

			if (max_inside - min_outside < threshold_peak) {
				_trans.erase(_trans.begin() + i);
			}
			else
				i++;
		}

	}
	else {
		transitions trans_to_add;

		for (size_t i = 0; i <= _trans.size(); ++i) {
			double beg = i<_trans.size() ? _trans[i]._beg : _diffs.back()._frame;
			double end = i>0 ? _trans[i - 1]._end : -0.5;
			if (beg - end > threshold_time) {
				beg -= threshold_time/2;
				end += threshold_time/2;
				for (double j = end * 2 + 1; j <= beg * 2 - 1; ++j) {
					const diff& d = _diffs[int(j)];
					if (d[w] > threshold) {
						trans_to_add.emplace_back(d._frame, d._frame);
					}
				}
			}
		}

		// Transitions filtering: if is connected to the previous one, remove it
		for (size_t i = 1; i < trans_to_add.size();) {
			if (trans_to_add[i]._beg - trans_to_add[i - 1]._end < 1) {
				trans_to_add[i - 1]._end = trans_to_add[i]._end;
				trans_to_add.erase(trans_to_add.begin() + i);
			}
			else
				i++;
		}

		// Transition validation
		for (size_t i = 0; i < trans_to_add.size();) {
			// Maximum within the transition
			double max_inside = 0;
			for (double j = trans_to_add[i]._beg * 2; j <= trans_to_add[i]._end * 2; ++j) {
				if (max_inside < _diffs[int(j)][w])
					max_inside = _diffs[int(j)][w];
			}
			// Minimum outside the transition at distance 2*w+1 on both sides
			int before = max(0, int(trans_to_add[i]._beg * 2 - (2 * w + 1)));
			int after = min(int(trans_to_add[i]._end * 2 + (2 * w + 1)), int(_diffs.size() - 1));
			double min_outside = min(_diffs[before][w], _diffs[after][w]);

			if (max_inside - min_outside < threshold_peak) {
				trans_to_add.erase(trans_to_add.begin() + i);
			}
			else
				i++;
		}

		// Add new transitions
		for (size_t i = 0; i < trans_to_add.size(); ++i) {
			auto it = lower_bound(_trans.begin(), _trans.end(), trans_to_add[i],
				[](const transition& a, const transition& b) {
				return a._end < b._beg;
			}
			);
			_trans.insert(it, trans_to_add[i]);
		}
	}
}
