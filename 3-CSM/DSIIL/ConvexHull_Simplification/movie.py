import os
import csv
import random

class Movie( object ):
    def __init__(self, movie_title, dataset_type, should_jitter_colors, jitter_offset):
        self.dataset_type = dataset_type
        self.movie_title = movie_title
        self.shot_lengths = []
        self.normalized_shot_lengths = []
        self.shot_start_end_frames = []       
        self.shot_counts = -1
        self.shot_colors = []
        self.weighted_shot_colors = []
        self.should_jitter_colors = should_jitter_colors
        self.jitter_offset = jitter_offset
        self.weights = []


    def read_shot_information(self):
        shot_txt_path = os.path.join('..', 'results', 'semi-master-shots', self.dataset_type, '%s_shots.txt' % self.movie_title)

        with open(shot_txt_path, 'r') as reader:
            for line in reader:
                start, end = line.strip().split('\t')
                self.shot_lengths.append(int(end)-int(start)+1)
                self.shot_start_end_frames.append((int(end), int(start)))

        self.shot_counts = len(self.shot_lengths)

        # shot length normalize from [min(l) max(l)] to [1 k]
        self.normalized_shot_lengths = [int(round(l/float(min(self.shot_lengths)))) for l in self.shot_lengths]


    def read_shot_colors(self, c_weight, r_weight, s_weight):
        color_csv_base_path = os.path.join('..', 'results', 'clustering', self.dataset_type, '%s', '%s-%d-colors.csv')
        for shot_idx in range(self.shot_counts):
            color_csv_path = color_csv_base_path % (self.movie_title, self.movie_title, shot_idx+1)

            with open(color_csv_path, 'r') as reader:
                reader.readline() # skip first line: hex
                for line in reader:
                    hex_color = line.lstrip('#')
                    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    self.shot_colors.append(rgb_color)
                    self.weights.append(self.normalized_shot_lengths[shot_idx])
                    for idx in range(self.normalized_shot_lengths[shot_idx]):
                        if self.should_jitter_colors:
                            rgb_offset = (random.randrange(-self.jitter_offset, self.jitter_offset+1),
                                random.randrange(-self.jitter_offset, self.jitter_offset+1),
                                random.randrange(-self.jitter_offset, self.jitter_offset+1))
                            new_rgb_color = tuple(map(lambda x, y: max(min(x+y, 255), 0), rgb_color, rgb_offset))

                            self.weighted_shot_colors.append(new_rgb_color)
                        else:
                            self.weighted_shot_colors.append(rgb_color)

## For test
# if __name__ == "__main__" :
#     m = Movie('la_la_land')
#     m.read_shot_information()
#     m.read_shot_colors('brisque', 'localglobal', 0.5, 1.0, 0.1)
#     print(len(m.weighted_shot_colors))
#     # print(m.shot_counts)