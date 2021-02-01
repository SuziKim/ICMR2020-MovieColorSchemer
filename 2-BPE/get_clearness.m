% Author: Suzi Kim (kimsuzi@kaist.ac.kr)
% Date: 2019. 01. 21 (Mon)
%
% Function: get_clearness
% Input: Shot
% Output: Clearness Cost

% - A metric representing how clear a shot is without blur.
% - Image sharpness measure

function clearness_costs = get_clearness(frames, clearness_cost_mode)

% BRISQUE: https://kr.mathworks.com/help/images/ref/brisque.html
% PIQE: https://kr.mathworks.com/help/images/ref/piqe.html
% NIQE: https://kr.mathworks.com/help/images/ref/niqe.html
% Gradient-based: https://kr.mathworks.com/matlabcentral/fileexchange/32397-sharpness-estimation-from-image-gradients

frame_count = size(frames, 4);
clearness_costs = zeros(frame_count, 1);

for i = 1:frame_count
    frame = frames(:, :, :, i);

    switch clearness_cost_mode
        case 'brisque'
            % normalize brisque which is usually in the range [0, 100]
            lambda_eq = @(x) [brisque(x.f) 1]*sparse(1+isnan(brisque(x.f)),1,1,2,1);
            clearness_costs(:) = arrayfun(lambda_eq, frame_structure);

        case 'piqe'
            clearness_costs(i) = piqe(frame);

        case 'niqe'
            clearness_costs(i) = niqe(frame);

        case 'gradient'
            G = double(rgb2gray(frame));
            [Gx, Gy] = gradient(G);
            S = sqrt(Gx.*Gx+Gy.*Gy);
            clearness_costs(i) = sum(sum(S))./(numel(Gx));

        otherwise
            warning('Unexpected clearness estimation mode.')
    end
end

end
