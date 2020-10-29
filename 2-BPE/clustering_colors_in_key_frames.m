% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
% 
% Function: clustering_colors_in_key_frames
% Input: Keyframes, Saliency Maps, Color Counts
% Output: Color Scheme

function color_scheme = clustering_colors_in_key_frames(key_frames, saliency_maps_of_key_frames, color_counts)

% CONSTANTS
use_rgb = 1;
use_ab_only = 0;

if use_rgb == 1
    nrows = size(key_frames,1);
    ncols = size(key_frames,2);
    keyframe_counts = size(key_frames, 4);
    
    key_frames = permute(key_frames, [1 2 4 3]);
    key_frames = reshape(key_frames, nrows*ncols*keyframe_counts, 3);

    % Apply the saliency as the probability of the color existance
    reshaped_saliency_maps = reshape(saliency_maps_of_key_frames, nrows*ncols*keyframe_counts, 1);
    probability_maps = reshaped_saliency_maps / max(reshaped_saliency_maps);
    is_included = zeros(size(probability_maps), 'logical');
    for probability_idx = 1:size(probability_maps, 1)
        probability = probability_maps(probability_idx);
        is_included(probability_idx) = logical(randsample([0, 1], 1, true, [1-probability, probability]));
    end

    survived_rgb = double(key_frames(is_included, :));

    % Perform K-means clustering
    [~, cluster_center] = kmeans(survived_rgb, color_counts, ...
                                          'distance', 'sqEuclidean', ...
                                          'Replicates', 3);

    color_scheme = uint8(cluster_center);
    disp('[clustering_colors_in_key_frames] Picked color scheme')
    disp(color_scheme)
else
    % LAB color information extraction

    lab_key_frames = rgb2lab(key_frames);

    if use_ab_only == 1
        ab_key_frames = lab_key_frames(:,:,2:3);
        nrows = size(ab_key_frames,1);
        ncols = size(ab_key_frames,2);
        key_frames = reshape(ab_key_frames, nrows*ncols, 2);
    else
        nrows = size(lab_key_frames,1);
        ncols = size(lab_key_frames,2);
        key_frames = reshape(lab_key_frames, nrows*ncols, 3);
    end

    % Apply the saliency as the probability of the color existance
    reshaped_saliency_maps = reshape(saliency_maps_of_key_frames, nrows*ncols, 1);
    probability_maps = reshaped_saliency_maps / max(reshaped_saliency_maps);
    is_included = zeros(size(probability_maps), 'logical');
    for probability_idx = 1:size(probability_maps, 1)
        probability = probability_maps(probability_idx);
        is_included(probability_idx) = logical(randsample([0, 1], 1, true, [1-probability, probability]));
    end

    survived_lab = key_frames(is_included, :);

    % Perform K-means clustering
    [~, cluster_center] = kmeans(survived_lab, color_counts, ...
                                          'distance', 'sqEuclidean', ...
                                          'Replicates', 3);

    color_scheme = lab2rgb(cluster_center, 'OutputType', 'uint8');
    disp('[clustering_colors_in_key_frames] Picked color scheme')
    disp(color_scheme)
end

end
