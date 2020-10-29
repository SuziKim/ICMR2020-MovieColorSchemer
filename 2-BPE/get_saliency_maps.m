% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 03. 21 (Thu)
%
% Function: get_saliency_maps
% Input: Frame No., video name
% Output: Saliency Maps

function saliency_maps = get_saliency_maps(saliency_base_path, shot_no, frames_no)
% ex) saliency_base_path: saliencies/dataset_type/movie_name

base_shot_dir = sprintf('shot-%d', shot_no);
output_path = fullfile(saliency_base_path, base_shot_dir);

query_counts = size(frames_no, 2);

basic_saliency_map_file = imread(fullfile(output_path, sprintf('%d-saliency.jpg', frames_no(1))));
saliency_maps = zeros([query_counts, size(basic_saliency_map_file)]);

for frame_no_idx = 1:query_counts
    saliency_map_file_name = sprintf('%d-saliency.jpg', frames_no(frame_no_idx));

    output_file_path = fullfile(output_path, saliency_map_file_name);
    saliency_maps(frame_no_idx, :, :) = im2double(imread(output_file_path));
end
