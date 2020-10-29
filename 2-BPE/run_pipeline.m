% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)

function run_pipeline(dataset_type, video_file_name, ...
    color_counts, frame_sampling_mode, keyframe_selection_mode, ...
    clearness_cost_mode)

% Turn off warnings
warning('off', 'stats:kmeans:FailedToConvergeRep');
warning('off', 'images:brisque:expectFiniteFeatures');

% Constants
RESULT_DIR = 'results';
VIDEO_DIR = 'videos';
RESULT_SALIENCY_DIR = 'saliencies';
RESULT_CLUSTERING_DIR = 'clustering';

input_video_file_path = fullfile(VIDEO_DIR, string(dataset_type), video_file_name);
[~, input_video_file_name, ~] = fileparts(input_video_file_path);

shot_segmentation_file_path = fullfile(RESULT_DIR, 'semi-master-shots', string(dataset_type), strcat(input_video_file_name, '_shots.txt'));
% convertStringsToChars

% Read shot segmentation txt file
disp('[run_pipeline] Reading a semi-master-shots')
shot_txt_file_id = fopen(shot_segmentation_file_path);
shots = textscan(shot_txt_file_id, '%d\t%d');
fclose(shot_txt_file_id);

% Color scheme list
shot_counts = size(shots{1}, 1);
color_scheme_list = zeros(shot_counts, color_counts, 3);

% Read video
disp('[run_pipeline] Reading a video')
input_video = VideoReader(input_video_file_path);

% Save all frames to estimate the saliency map 
disp('[run_pipeline] Saving all frames of the video')
saliency_base_path = fullfile(RESULT_DIR, RESULT_SALIENCY_DIR, string(dataset_type), input_video_file_name);
save_all_frames(input_video, saliency_base_path, shot_counts, shots);

disp('[run_pipeline] Estimating saliency of all frame')
estimate_saliency_map(saliency_base_path, shot_counts);


% Generate a directory to save clustering results of the BPE
csv_video_dir = fullfile(RESULT_DIR, RESULT_CLUSTERING_DIR, string(dataset_type), input_video_file_name);
if ~exist(csv_video_dir, 'dir')
    mkdir(csv_video_dir);
end
        
for shot_no = 1:shot_counts
    fprintf('[run_pipeline] Cost calculation %d-th shot\n', shot_no)
    
    shot_begin_frame_index = shots{1}(shot_no) + 1;
    shot_end_frame_index = shots{2}(shot_no) + 1;

    if shot_no == shot_counts
        num_Frames = get(input_video, 'numberOfFrames');
        shot = read(input_video, [shot_begin_frame_index num_Frames]);
        shot_struct = {shot_begin_frame_index:1:num_Frames; shot};
    else
        shot = read(input_video, [shot_begin_frame_index, shot_end_frame_index]);
        shot_struct = {shot_begin_frame_index:1:shot_end_frame_index; shot};
    end
        
    [color_scheme_list(shot_no, :, :), shot_costs] = extract_color_scheme_from_shot(shot_struct, shot_no, frame_sampling_mode, ...
        keyframe_selection_mode, color_counts, clearness_cost_mode, saliency_base_path);   

    % Save title-shotno-costs.csv
    cost_file_ID = fopen(fullfile(csv_video_dir, sprintf('%s-%d-costs.csv', input_video_file_name, shot_no)),'w');
    fprintf(cost_file_ID, 'frameNo, KF, Clearness, Saliency, Representativeness\n');
    fprintf(cost_file_ID, '%d, %d, %f, %f, %f\n', shot_costs');
    fclose(cost_file_ID);

    % Save title-shotno-colors.csv
    color_file_ID = fopen(fullfile(csv_video_dir, sprintf('%s-%d-colors.csv', input_video_file_name, shot_no)),'w');
    fprintf(color_file_ID, 'hex\n');   
    shot_colors_rgb = color_scheme_list(shot_no, :, :);
    shot_colors_rgb = reshape(shot_colors_rgb, [size(shot_colors_rgb, 2), size(shot_colors_rgb, 3)]);

    shot_colors_hsl = rgb2hsl(double(shot_colors_rgb)/255.0);
    shot_colors_hsl = sortrows(shot_colors_hsl, [-3 -1 -2]);
    shot_colors_rgb = uint8(hsl2rgb(shot_colors_hsl)*255);

    shot_colors_hex = rgb2hex(shot_colors_rgb);
    for shot_color_hex_idx = 1:color_counts
        fprintf(color_file_ID, sprintf('%s\n', shot_colors_hex(shot_color_hex_idx, :)));
    end    
    fclose(color_file_ID);

    color_scheme_img_width = 100;
    color_scheme_img = zeros(color_scheme_img_width, color_scheme_img_width*color_counts, 3);
    for i = 1:color_counts
        color_scheme_img(:, 1+(i-1)*color_scheme_img_width:i*color_scheme_img_width, :) = double(repmat(reshape(shot_colors_rgb(i, :), [1 1 3]), color_scheme_img_width, color_scheme_img_width, 1)) / 255.0;
    end
    img_file_name = fullfile(csv_video_dir, sprintf('%s-%d-colors.jpg', input_video_file_name, shot_no));
    imwrite(color_scheme_img, img_file_name);
    
    clear shot;
end


% Turn on warnings
warning('on', 'stats:kmeans:FailedToConvergeRep');
warning('on', 'images:brisque:expectFiniteFeatures');

clear variables;
end