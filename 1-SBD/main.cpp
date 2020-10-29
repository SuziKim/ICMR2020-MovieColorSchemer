#include <iostream>
#include <iomanip>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <string>

#include "infix_iterator.h"

#include "frame_buffer.h"
#include "evaluator.h"
#include "thresholder.h"

#include <filesystem>

using namespace cv;
using namespace std;
using namespace std::tr2::sys;


inline string zero_padded_string(int _Val, int _MinLength)
{	// convert int to string with leading zeros
	char _Buf[2 * _MAX_INT_DIG];

	sprintf_s(_Buf, sizeof(_Buf), "%0*d", _MinLength, _Val);
	return (string(_Buf));
}

void resize_prop_rect(InputArray src, OutputArray dst, Size dsize, int interpolation = INTER_LINEAR) {
	Size ssize = src.size();

	double xscale = double(dsize.width) / ssize.width;
	double yscale = double(dsize.height) / ssize.height;

	double scale = min(xscale, yscale);

	resize(src, dst, Size(), scale, scale, interpolation);
}

double extract_boundary(string video_filename, string input_prefix, Size max_image_size, double W, double threshold, double threshold_time, double threshold_peak, bool should_save_file) {
	// Open video 
	VideoCapture cap(video_filename);
	if (!cap.isOpened()) {
		std::cerr << "Unable to open video.\n";
		exit(EXIT_FAILURE);
	}

	string gt_filename = input_prefix + "_gt.txt";
	string comparison_filename = input_prefix + "_comparison.txt";

	// ICMR2020-Suzi: Adding the parameter information into file names
	std::stringstream strstr;
	if (false) // ICMR2020-Suzi: Only true for the exp1
		strstr << std::fixed << std::setprecision(1) << "_w-" << W << "_t-" << threshold << "_ts-" << threshold_time;
	std::string params = strstr.str();

	string diffs_filename = input_prefix + params + "_diffs.txt";
	string trans_filename = input_prefix + params + "_trans.txt";
	string shots_filename = input_prefix + params + "_shots.txt";
	string shots_subtitle_filename = input_prefix + params + "_shots.srt";

	// Save all frames
	if (false) {
		Mat3b img;
		int i = 0;
		path folder_name = input_prefix;
		create_directory(folder_name);

		int nframes = static_cast<int>(cap.get(CAP_PROP_FRAME_COUNT));
		int nchar = static_cast<int>(to_string(nframes).size());

		while (true) {
			if (i % 1000 == 0)
				cout << "\r" << i << " - " << i + 999;
			cap >> img;
			if (img.empty())
				return 0;
			resize_prop_rect(img, img, max_image_size, INTER_AREA);
			path filename = zero_padded_string(i, nchar) + ".png";
			// ICMR2020-Suzi: change the usage of the std library
			imwrite(string(folder_name / filename), img);
			i++;
		}
		return 0;
	}

	// Ground truth vector
	transitions trans;

	cout << "Ground truth file (" << gt_filename << ") ";
	ifstream is_gt(gt_filename);
	if (is_gt) {
		cout << "found.\n";

		transitions shots;
		copy(istream_iterator<transition>(is_gt), istream_iterator<transition>(), back_inserter(shots));

		double nframes = cap.get(CAP_PROP_FRAME_COUNT);
		for (int i = 1; i < shots.size(); ++i) {
			trans.emplace_back(shots[i - 1]._end + 0.5, shots[i]._beg - 0.5);
		}
		if (shots.back()._end < nframes - 1)
			trans.emplace_back(shots.back()._end + 0.5, nframes - 1);
	}
	else {
		cout << "not found.\n";
	}

	// Comparison vector
	transitions trans_comparison;

	cout << "Comparison file (" << comparison_filename << ") ";
	ifstream is_comparison(comparison_filename);
	if (is_comparison) {
		cout << "found.\n";

		transitions shots;
		copy(istream_iterator<transition>(is_comparison), istream_iterator<transition>(), back_inserter(shots));

		double nframes = cap.get(CAP_PROP_FRAME_COUNT);
		for (int i = 1; i < shots.size(); ++i) {
			trans_comparison.emplace_back(shots[i - 1]._end + 0.5, shots[i]._beg - 0.5);
		}
		if (shots.back()._end < nframes - 1)
			trans_comparison.emplace_back(shots.back()._end + 0.5, nframes - 1);
	}
	else {
		cout << "not found.\n";
	}

	// Differences vector
	vector<diff> diffs;

	cout << "Differences file (" << diffs_filename << ") ";
	ifstream is_diffs(diffs_filename);
	if (is_diffs) {
		cout << "already present: video won't be analyzed.\n";
		cout << "Reading differences... ";

		copy(istream_iterator<diff>(is_diffs), istream_iterator<diff>(), back_inserter(diffs));

		cout << "done.\n";
	}
	else {
		cout << "not found: video will be analyzed.\n";
		cout << "Analyzing video... \n";

		int index = -1;
		frame_buffer fb(W);

		while (true) {
			index++;
			if (index % 1000 == 0)
				cout << "\r" << index << " - " << index + 999;

			// Limit maximum number of frames to be analyzed
			//if (index == 4000)
			//	break;

			Mat3b img;
			cap >> img;
			if (img.empty())
				break;
			resize_prop_rect(img, img, max_image_size, INTER_AREA);
			fb.push_back(img);

			if (index >= int(W)) {
				if (index - W > 0)
					diffs.push_back(fb.get_diffs(index - W - 0.5));
				diffs.push_back(fb.get_diffs(index - W));
			}

		}
		cout << "\n";
		cout << "done.\n";

		if (should_save_file) {
			cout << "Writing differences... ";

			ofstream os_diffs(diffs_filename, ofstream::out);
			if (!os_diffs) {
				cerr << "Unable to open differences file for writing.\n";
				exit(EXIT_FAILURE);
			}

			copy(diffs.begin(), diffs.end(), ostream_iterator<diff>(os_diffs, "\n"));
			cout << "done.\n";
		}		
	}

	// ICMR2020-Suzi: Adding the parameter information into the file names
	string ev_filename = input_prefix + params + "_eval.txt";
	ofstream os_ev;
	if (should_save_file) {
		if (!trans.empty()) {
			os_ev.open(ev_filename);
		}
	}

	vector<vector<int>> out_trans(diffs.size(), vector<int>(2 * W, 0));

	thresholder thr(diffs);
	for (double w = 0.5; w <= W; w += 0.5) {
		thr.apply(w, threshold, threshold_time, threshold_peak);

		for (const auto& tran : thr._trans) {
			for (double frame = tran._beg; frame <= tran._end; frame += 0.5) {
				out_trans[int(frame * 2)][int(w * 2 - 1)] = 140;
			}
		}

		if (!trans.empty()) {
			evaluator ev(trans, thr._trans);
			double precision = double(ev._p._tot._num[0]) / (double(ev._p._tot._num[0]) + double(ev._p._tot._num[1]));
			double recall = double(ev._p._tot._num[0]) / (double(ev._p._tot._num[0]) + double(ev._p._tot._num[2]));
			double F1 = 2 * precision*recall / (precision + recall);
			cout << "W      :\t" << w << "\n";
			cout << "Total  :\t" << ev._p._tot << "\t" << F1 << "\n";
			cout << "Abrupt :\t" << ev._p._split[transition::abrupt] << "\n";
			cout << "Gradual:\t" << ev._p._split[transition::gradual] << "\n";
			cout << "\n";

			// ICMR2020-Suzi: Change the logging string
			if (should_save_file) {
				os_ev << "W      :\t" << w << "\n";
				os_ev << "Total  :\t" << ev._p._tot << "\t" << F1 << "\n";
				os_ev << "Abrupt :\t" << ev._p._split[transition::abrupt] << "\n";
				os_ev << "Gradual:\t" << ev._p._split[transition::gradual] << "\n";
				os_ev << "\n";
			}
		}
	}

	if (!trans_comparison.empty()) {
		evaluator ev(trans, trans_comparison);
		double precision = double(ev._p._tot._num[0]) / (double(ev._p._tot._num[0]) + double(ev._p._tot._num[1]));
		double recall = double(ev._p._tot._num[0]) / (double(ev._p._tot._num[0]) + double(ev._p._tot._num[2]));
		double F1 = 2 * precision*recall / (precision + recall);
		cout << "Comparison with " << comparison_filename << ":\n";
		cout << "Total  :\t" << ev._p._tot << "\t" << F1 << "\n";
		cout << "Abrupt :\t" << ev._p._split[transition::abrupt] << "\n";
		cout << "Gradual:\t" << ev._p._split[transition::gradual] << "\n";
		cout << "\n";
	}

	if (should_save_file) {
		cout << "\tWriting transitions (" << trans_filename << ")... ";
		ofstream os_trans(trans_filename);
		if (!os_trans) {
			cerr << "Unable to open transitions file for writing.\n";
			exit(EXIT_FAILURE);
		}
		for (const auto& t : out_trans) {
			copy(t.begin(), t.end(), infix_ostream_iterator<int>(os_trans, "\t"));
			os_trans << "\n";
		}

		cout << "done.\n";
	}	

	double nframes = cap.get(CAP_PROP_FRAME_COUNT);
	double fps = cap.get(CAP_PROP_FPS);

	double total_shot_length = 0;
	int shot_count = 0;

	if (true) {
		cout << "\tWriting shots (" << shots_filename << ")... \n";

		double nframes = cap.get(CAP_PROP_FRAME_COUNT);

		transitions shots;
		double beg = 0;
		for (const auto& x : thr._trans) {
			// ICMR2020-Suzi: We handle the edge case of ILSD.
			if (floor(x._beg - 0.5) > beg) {
				shots.emplace_back(beg, floor(x._beg - 0.5));
				total_shot_length += floor(x._beg - 0.5) - beg;
				shot_count++;
			}

			beg = ceil(x._end + 0.5);
		}
		if (beg < nframes - 1) {
			shots.emplace_back(beg, nframes - 1);
			total_shot_length += nframes - 1 - beg;
			shot_count++;
		}

		if (should_save_file) {
			ofstream os_shots(shots_filename);
			if (!os_shots) {
				cerr << "Unable to open shots file for writing.\n";
				exit(EXIT_FAILURE);
			}

			copy(shots.begin(), shots.end(), ostream_iterator<transition>(os_shots));

			cout << "done.\n";
		}
	}

	// ICMR2020-Suzi: We generate a subtitle file (.srt) to check the segmentation results visually
	if (should_save_file) {
		if (true) {
			cout << "\tWriting shots (" << shots_filename << ")...  to srt file";

			transitions shots;
			double beg = 0;
			for (const auto& x : thr._trans) {
				shots.emplace_back(beg, floor(x._beg - 0.5));
				beg = ceil(x._end + 0.5);
			}
			if (beg < nframes - 1)
				shots.emplace_back(beg, nframes - 1);

			ofstream os_shots(shots_subtitle_filename);
			if (!os_shots) {
				cerr << "Unable to open shots subtitle file for writing.\n";
				exit(EXIT_FAILURE);
			}

			int shotCount = 1;
			for (transitions::iterator it = shots.begin(); it != shots.end(); it++) {
				// write sequence number
				// ex) 3
				os_shots << shotCount << endl;

				// write two-hash arrow to separate beginning and end timecodes
				// ex) 00:00:00,000 --> 00:00:04,440
				int start_total_milliseconds = it->_beg / fps * 1000;
				int start_milliseconds = start_total_milliseconds % 1000;
				int start_seconds = (start_total_milliseconds / 1000) % 60;
				int start_minutes = ((start_total_milliseconds / 1000) / 60) % 60;
				int start_hours = (start_total_milliseconds / 1000) / 60 / 60;

				int end_total_milliseconds = it->_end / fps * 1000;
				int end_milliseconds = end_total_milliseconds % 1000;
				int end_seconds = (end_total_milliseconds / 1000) % 60;
				int end_minutes = ((end_total_milliseconds / 1000) / 60) % 60;
				int end_hours = (end_total_milliseconds / 1000) / 60 / 60;

				os_shots << setfill('0') << setw(2) << start_hours << ":"
					<< setfill('0') << setw(2) << start_minutes << ":"
					<< setfill('0') << setw(2) << start_seconds << ","
					<< setfill('0') << setw(3) << start_milliseconds << " --> "
					<< setfill('0') << setw(2) << end_hours << ":"
					<< setfill('0') << setw(2) << end_minutes << ":"
					<< setfill('0') << setw(2) << end_seconds << ","
					<< setfill('0') << setw(3) << end_milliseconds << endl;

				// write caption text
				// ex) Shot#1
				os_shots << "Shot #" << shotCount << endl;

				// write blank line to separate caption sequence
				os_shots << endl;

				shotCount++;
			}

			os_shots.close();

			cout << "done.\n";
		}
	}

	cap.release();
	
	cout << "[Results] total shot length: " << total_shot_length << " / FPS: " << fps << " / #ofShots: " << shot_count << "\n";
	return total_shot_length / fps / shot_count;
}

double calculate_average_threshold_time(Size max_image_size, string video_filename) {
	cout << "calculate_average_threshold_time\n";

	string input_prefix = video_filename.substr(0, video_filename.rfind('.'));
	const double w = 2.5;
	const double threshold = 80;
	const double threshold_time = 20.0;
	const double threshold_peak = threshold / 2.0;

	double average_shot_length = extract_boundary(video_filename, input_prefix, max_image_size, w, threshold, threshold_time, threshold_peak, false);
	cout << "finishing calculate_average_threshold_time: " << average_shot_length << "\n\n";
	return average_shot_length;
}

int main (int argc, const char *argv[])
{ 
	// Maximum image size: video will be scaled to this resolution
	const Size max_image_size(320, 180);

	// ICMR2020-Suzi: Get an additional arguments; threshold(T)
	// Parameter parsing 
	if (argc != 4) {
		cout << "Syntax:\n\n";
		cout << "SBD <input_video> <W_size> <threshold>\n\n";
		exit(EXIT_FAILURE);
	}

	// Algorithm parameters
	string video_filename(argv[1]);
	
	// ICMR2020-Suzi: We modified the type of W from integer to float.
	const double W = atof(argv[2]);
	
	// ICMR2020-Suzi: Parsing the threshold arguments.
	const double threshold = atof(argv[3]);
	const double threshold_time = calculate_average_threshold_time(max_image_size, video_filename);
	const double threshold_peak = threshold / 2.0;

	// ICMR2020-Suzi: Change the output path
	// Find files prefix
	string video_input_prefix = video_filename.substr(0, video_filename.rfind('.'));
	path video_input_path = path(video_input_prefix);
	string video_input_prefix_parent_path = video_input_path.parent_path();
	path video_input_prefix_filename = video_input_path.filename();

	string original_video_path("videos");
	path result_path = path("results") / path("semi-master-shots");
	path result_directory = video_input_prefix_parent_path.replace(0, original_video_path.length() + 2, result_path);
	create_directories(result_directory);
	string input_prefix = result_directory / video_input_prefix_filename;

	double average_shot_length = extract_boundary(video_filename, input_prefix, max_image_size, W, threshold, threshold_time, threshold_peak, true);
}
