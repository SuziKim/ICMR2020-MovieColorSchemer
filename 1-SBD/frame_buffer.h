#if !defined FRAME_BUFFER_H
#define FRAME_BUFFER_H

#include "frame_info.h"
#include "differences.h"

struct frame_buffer {
	std::vector<frame_info> _buf;
	const size_t _w, _max_size;
	size_t _head;
	int _idx_head;

	frame_buffer(size_t w) : _w(w), _max_size(2 * w + 1), _head(0), _idx_head(-int(w) - 1) {}

	bool full() const {
		return _buf.size() == _max_size;
	}

	void push_back(const cv::Mat3b& img) {
		frame_info fi(img);
		fi._diff.resize(_w, 0.0);
		fi._diff_shift.resize(_w, 0.0);

		if (_buf.empty()) {
			for (size_t w = 0; w < _w + 2; ++w) 
				_buf.push_back(fi);
		}
		else if (_buf.size() < 2 * _w + 1) {
			// Buffer was just created: still cannot compute differences
			_buf.push_back(fi);
		}
		else {
			// Buffer is full, let's compute the differences
			_buf[_head] = fi;
			calcDiff(bufpos(int(_head - _w)));
			_head = bufpos(int(_head + 1));
			_idx_head++;
		}
	}

	const frame_info& at(size_t frame) const {
		assert(full());

		frame -= _idx_head;
		//assert(frame >= _w && frame < 2 * _w);

		return _buf[bufpos(int(_head + frame))];
	}
	const frame_info& operator[](size_t frame) const {
		return at(frame);
	}
	
	double Mnw(double n, double w) const {
		if (n + w == int(n + w)) {
			if (n == int(n))
				return at(int(n))._diff[int(w - 1)];
			else
				return at(int(n))._diff_shift[int(w)];
		}
		else {
			double a, b;

			if (n == int(n)) {
				a = at(int(n - 1))._diff_shift[int(w)];
				b = at(int(n))._diff_shift[int(w)];
			}
			else {
				a = at(int(n - 0.5))._diff[int(w - 1)];
				b = at(int(n + 0.5))._diff[int(w - 1)];
			}

			return 0.5*(a + b);
		}
	}
	
	diff get_diffs(double frame) const {
		assert(frame == _idx_head + _w || frame == _idx_head + _w - 0.5);
		diff d(frame,_w);
		for (double w = 0.5; w <= _w; w += 0.5)
			d[w] = Mnw(frame, w);
		return d;
	}

private:
	size_t bufpos(int pos) const {
		assert(pos >= -int(_max_size));
		return (pos + _max_size) % _max_size;
	}

	double calcPixDist(const cv::Mat1b& imga, const cv::Mat1b& imgb) {
		cv::Mat1b diff;
		absdiff(imga, imgb, diff);
		pow(diff, 2, diff);
		return sum(diff)[0] / (imga.rows*imga.cols);
	}

	double calcHistDist(const std::array<std::vector<double>, 3>& hista, const std::array<std::vector<double>, 3>& histb) {
		double d = 0.0;
		for (size_t c = 0; c < 3; ++c) {
			for (size_t i = 0; i < frame_info::N; ++i) {
				double bin_max = std::max(hista[c][i], histb[c][i]);
				if (bin_max>0.0) {
					double bin_diff = hista[c][i] - histb[c][i];
					d += bin_diff*bin_diff / bin_max;
				}
			}
		}
		return d;
	}

	void calcDiff(size_t pos) {
		for (size_t w = 1; w <= _w; ++w) {
			frame_info& fia = _buf[bufpos(int(pos - w))];
			frame_info& fib = _buf[bufpos(int(pos + w))];

			double d_sigma = calcPixDist(fia._img, fib._img);
			double d_chisquared = calcHistDist(fia._histo, fib._histo);

			_buf[pos]._diff[w - 1] = 0.5*d_sigma + 0.5*d_chisquared;

			frame_info& fia_shift = _buf[bufpos(int(pos - w + 1))];
			d_sigma = calcPixDist(fia_shift._img, fib._img);
			d_chisquared = calcHistDist(fia_shift._histo, fib._histo);

			_buf[pos]._diff_shift[w - 1] = 0.5*d_sigma + 0.5*d_chisquared;
		}
	}
};

#endif // FRAME_BUFFER_H 