% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)

function estimate_saliency_map(saliency_base_path, shot_counts)
% ex) saliency_base_path: results/saliencies/dataset_type/movie_name

% saliency extraction
base_command = "THEANO_FLAGS='cuda.root='/usr/local/cuda',cuda.include_path='/usr/local/cuda/include',dnn.base_path='/usr/local/cuda',dnn.include_path='/usr/local/cuda/include',dnn.library_path='/usr/local/cuda/lib64',dnn.bin_path='/usr/local/cuda/lib64',mode=FAST_RUN,device=cuda,floatX=float32,optimizer_including=cudnn' python saliency-salgan-2017/scripts/03-predict.py -i %s -c %d";
command_str = sprintf(base_command, saliency_base_path, shot_counts);
[status, command_out] = system(command_str, '-echo');

if status ~= 0
    disp('Error Occured During Saliency Generation');
    fprintf('%s\n', command_out);
end

end

