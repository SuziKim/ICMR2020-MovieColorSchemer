% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)

function save_all_frames(input_video, saliency_base_path, shot_counts, shots)
% ex) saliency_base_path: results/saliencies/dataset_type/movie_name

if ~exist(saliency_base_path, 'dir')
    mkdir(saliency_base_path)
end

for shot_no = 1:shot_counts
    fprintf('  - Saving %d-th/%d shot\n', shot_no, shot_counts)

    shot_begin_frame_index = shots{1}(shot_no) + 1;
    shot_end_frame_index = shots{2}(shot_no) + 1;

    if shot_no == shot_counts
        num_Frames = get(input_video, 'numberOfFrames');
        shot = read(input_video, [shot_begin_frame_index num_Frames]);
    else
        shot = read(input_video, [shot_begin_frame_index, shot_end_frame_index]);
    end

    shot_dir = fullfile(saliency_base_path, sprintf('shot-%d', shot_no));

    if ~exist(shot_dir, 'dir')
        mkdir(shot_dir);
    end

    % save frames into images
    frame_count = size(shot, 4);
    if numel(dir(fullfile(shot_dir, '*-frame.jpg'))) ~= frame_count
        for frame_idx = 1:frame_count
            frame = shot(:, :, :, frame_idx);   
            imwrite(frame, fullfile(shot_dir, sprintf('%d-frame.jpg', frame_idx+shot_begin_frame_index-1)));
        end
    end

    clear shot;
end

end
