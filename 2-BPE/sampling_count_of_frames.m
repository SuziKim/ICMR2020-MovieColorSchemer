% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
%
% Function: sampling_count_of_frames
% Input: Frame Sampling Mode ('proportional', 'single', 'random')
% Output: Sampling Count of Frame

function frame_sampling_count = sampling_count_of_frames(mode, frame_count)

switch mode
    case 'single'
        frame_sampling_count = 3;
    case 'random'
        frame_sampling_count = randi(frame_count);
    case 'proportional'
        frame_count_proportional_constant = 0.02; % CONSTANT
        frame_sampling_count = max(1, frame_count * frame_count_proportional_constant);
    otherwise
        warning('Unexpected frame sampling mode.')
end
        
end