% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)

function [color_scheme, shot_costs] = extract_color_scheme_from_shot(shot_struct, shot_no, frame_sampling_mode, ...
    keyframe_selection_mode, color_counts, clearness_cost_mode, saliency_base_path)

frame_count = size(shot_struct{1}, 2);

frame_sampling_count = sampling_count_of_frames(frame_sampling_mode, frame_count);
fprintf('[extract_color_scheme_from_shot] Frame sampling count: %d\n', frame_sampling_count);

[key_frames_struct, shot_costs] = select_key_frames_from_shot(keyframe_selection_mode, shot_no, shot_struct, frame_sampling_count, ...
    clearness_cost_mode, saliency_base_path);

saliency_maps_of_key_frames = get_saliency_maps(saliency_base_path, shot_no, key_frames_struct{1});

color_scheme = clustering_colors_in_key_frames(key_frames_struct{2}, saliency_maps_of_key_frames, color_counts);

end 