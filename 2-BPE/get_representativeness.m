% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
%
% Function: get_representativeness
% Input: Shot
% Output: representativeness Cost

function representativeness_costs = get_representativeness(frames)
% How much the frame is insider? How similar with all frames it is.

% Constants
bin_counts_h = 50;
bin_counts_s = 50;
bin_counts_v = 50;

frame_counts = size(frames, 4);

hsv_frames = zeros(size(frames));
% Convert rgb to hsv images
for i = 1:frame_counts
    hsv_frames(:, :, :, i) = rgb2hsv(frames(:, :, :, i));
end

% Histogram calculation
h_edges = linspace(0, 1, bin_counts_h+1);
s_edges = linspace(0, 1, bin_counts_s+1);
v_edges = linspace(0, 1, bin_counts_v+1);

frame_hist = zeros(bin_counts_h + bin_counts_s + bin_counts_v, frame_counts);
for i = 1:frame_counts
    [N_h, ~, ~] = histcounts(hsv_frames(:, :, 1, i), 'NumBins', bin_counts_h, 'BinEdges', h_edges);
    [N_s, ~, ~] = histcounts(hsv_frames(:, :, 2, i), 'NumBins', bin_counts_s, 'BinEdges', s_edges);
    [N_v, ~, ~] = histcounts(hsv_frames(:, :, 3, i), 'NumBins', bin_counts_v, 'BinEdges', v_edges);

    frame_hist(:, i) = [N_h, N_s, N_v];
end

dist = zeros(1, frame_counts);
for i = 1:frame_counts
    dist(:, i) = sum(pdist2(frame_hist(:, i)', frame_hist(:, :)', 'Correlation'));
end

representativeness_costs = (max(dist)-  dist) / max(dist);

end
