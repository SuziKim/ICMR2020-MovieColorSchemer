#if !defined FRAME_INFO_H
#define FRAME_INFO_H

#include <opencv2/opencv.hpp>

#include <array>
#include <vector>

struct frame_info {
	static const unsigned N = 32;

	cv::Mat1b _img;
	std::array<std::vector<double>, 3> _histo;
	std::vector<double> _diff;
	std::vector<double> _diff_shift;

	frame_info(const cv::Mat3b& img) {
		cvtColor(img, _img, cv::COLOR_BGR2GRAY);
		calcHistogram(img);
	}

private:
	void calcHistogram(const cv::Mat3b& img) {
		int rows = img.rows;
		int cols = img.cols;

		for (size_t color = 0; color < 3; ++color) {
			_histo[color] = std::vector<double>(N, 0.0);
		}

		for (int r = 0; r < rows; ++r) {
			for (int c = 0; c < cols; ++c) {
				auto pix = img(r, c);
				for (int color = 0; color < 3; ++color) {
					_histo[color][pix[color] * N / 256]++;
				}
			}
		}

		for (size_t color = 0; color < 3; ++color) {
			for (size_t bin = 0; bin < N; ++bin) {
				_histo[color][bin] /= rows*cols;
			}
		}
	}
};

#endif // FRAME_INFO_H 