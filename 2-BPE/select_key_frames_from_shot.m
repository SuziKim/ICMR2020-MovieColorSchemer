% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
%
% Function: select_key_frames_from_shot
% Input: Shot, Frame Sampling Count, Selection Mode ('random', 'custom-cost')
% Output: Key Frames

function [key_frames_struct, costs] = select_key_frames_from_shot(mode, shot_no, shot_struct, ...
    frame_sampling_count, clearness_cost_mode, saliency_base_path)

frame_counts = size(shot_struct{1}, 2);
costs = zeros(frame_counts, 5);

switch mode
    case 'random'
        random_frame_indices = randperm(frame_counts, frame_sampling_count);
        key_frames_struct = {shot_struct{1}(1, random_frame_indices); shot_struct{2}(:, :, :, random_frame_indices)};        
        disp('[select_key_frames_from_shot] Selected key frames')
        disp(mat2str(random_frame_indices))
        
    case 'custom-cost'      
        clearness_costs_constant = 0.5; % CONSTANT
        saliency_costs_constant = 0.6; % CONSTANT
        representativeness_costs_constant = 0.8; % CONSTANT
        
        % A sampled frame must be a clear image without blur.
        clearness_costs = get_clearness(shot_struct{2}, clearness_cost_mode);

        % A sampled frame must show a high saliency.
        saliency_costs = get_saliency(saliency_base_path, shot_no, shot_struct);
        
        % A sampled frame must be a representative image.
        representativeness_costs = get_representativeness(shot_struct{2});
        
        costs(:, 1) = shot_struct{1};
        costs(:, 3) = clearness_costs;
        costs(:, 4) = saliency_costs;
        costs(:, 5) = representativeness_costs;
        
        weights = clearness_costs * clearness_costs_constant + ...
            representativeness_costs * representativeness_costs_constant + ...
            saliency_costs * saliency_costs_constant;
        
        [~, index] = sort(weights, 'descend');
        key_frames_struct = {shot_struct{1}(1, index(1:frame_sampling_count)); shot_struct{2}(:, :, :, index(1:frame_sampling_count))};
        
        costs(index(1:frame_sampling_count), 2) = 1;
        
        disp('[select_key_frames_from_shot] Selected key frames')
        disp(mat2str(index(1:frame_sampling_count)))
        
    otherwise
        warning('Unexpected key frame selection mode.')
end


end