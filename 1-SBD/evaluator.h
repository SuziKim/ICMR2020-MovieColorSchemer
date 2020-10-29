#if !defined EVALUATOR_H
#define EVALUATOR_H

#include <vector>
#include <array>

#include "transitions.h"

struct evaluator {
	enum perf_t { tp, fp, fn };

	struct perf {
		std::array<unsigned,3> _num;
		std::array<transitions,3> _trans;

		perf() : _num(), _trans() {}

		void operator() (perf_t type, const transition& t) {
			_num[type]++;
			_trans[type].push_back(t);
		}

		friend std::ostream& operator<< (std::ostream& os, const perf& p) {
			os << "TP: " << p._num[tp] << " / " << (p._num[tp] + p._num[fn]) << " - " << "FP : " << p._num[fp] << " - " << "FN : " << p._num[fn];
			return os;
		}

		std::ostream& log_trans(std::ostream& os, perf_t type) const {
			const auto& x = _trans[type];
			copy(x.begin(), x.end(), std::ostream_iterator<transition>(os));
			return os;
		}

		std::ostream& log_trans(std::ostream& os) const {
			os << "TP:\n";
			log_trans(os, evaluator::tp);
			os << "\nFP:\n";
			log_trans(os, evaluator::fp);
			os << "\nFN:\n";
			log_trans(os, evaluator::fn);
			os << "\n";
			return os;
		}
	};

	struct perfs {
		perf _tot;
		std::array<perf,2> _split;

		void operator() (perf_t type, const transition& t) {
			_tot(type, t);
			_split[t.type()](type, t);
		}
	};

	const transitions& _gt;
	const transitions& _found;

	perfs _p;

	evaluator(const transitions& gt, const transitions& found) : _gt(gt), _found(found) {
		auto it_gt = _gt.begin();
		auto it_found = _found.begin();

		while (it_gt != _gt.end() || it_found != _found.end()) {
			if (it_gt == _gt.end()) {
				_p(fp,*it_found);
				it_found++;
			}
			else if (it_found == _found.end()) {
				_p(fn,*it_gt);
				it_gt++;
			}
			else if (it_found->_end < it_gt->_beg) {
				_p(fp,*it_found);
				it_found++;
			}
			else if (it_found->_beg > it_gt->_end) {
				_p(fn,*it_gt);
				it_gt++;
			}
			else {
				_p(tp,*it_gt);
				it_found++;
				it_gt++;
			}
		}
	}

};

#endif // EVALUATOR_H 