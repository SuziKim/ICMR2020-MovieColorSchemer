% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
%
% Function: get_saliency
% Input: Shot
% Output: Saliency Cost

function saliency_costs = get_saliency(saliency_base_path, shot_no, shot_struct)

saliency_maps = get_saliency_maps(saliency_base_path, shot_no, shot_struct{1});
average_saliency_maps = mean(mean(saliency_maps, 2), 3);
saliency_costs = reshape(average_saliency_maps, [size(average_saliency_maps, 1), 1]);
   
end
