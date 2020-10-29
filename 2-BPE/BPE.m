% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2020. 10. 25 (Sun)

function BPE(dataset_type, video_file_name)
arguments
    dataset_type (1, 1) string
    video_file_name (1, 1) string
end
    
color_counts = 5;
frame_sampling_mode = 'single'; % for test, you can choose among ('proportional', 'random')
keyframe_selection_mode = 'custom-cost'; % for test, you can choose among ('random', 'custom-cost')
clearness_cost_mode = 'brisque'; % for test, you can choose among ('brisque', 'piqe', 'niqe', 'gradient')

if dataset_type ~= 'OVSD' && dataset_type ~= 'CMD'
   warning('Unexpected dataset type. It should be either OVSD or CMD.')
   return
end

disp('[BPE] Parameters Info')
fprintf('  - video_file_name: %s\n', video_file_name)
fprintf('  - color_counts: %d\n', color_counts)
fprintf('  - frame_sampling_mode: %s\n', frame_sampling_mode)
fprintf('  - keyframe_selection_mode: %s\n', keyframe_selection_mode)
fprintf('  - clearness_cost_mode: %s\n', clearness_cost_mode)

run_pipeline(dataset_type, video_file_name, color_counts, ... 
            frame_sampling_mode, keyframe_selection_mode, ...
            clearness_cost_mode);

end