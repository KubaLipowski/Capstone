%Image Processing
clear; clc;

%Break up full image into 81 tiles
day = '1'; %Replace with day timepoint
imageFile = strcat('MergedTile.tif'); %image file
Folder = strcat('C:\Users\student\Desktop\PC Lab\Day',day,'\', imageFile, ' tiles'); %folder for output

mkdir([Folder])
file = strcat('\s', num2str(section), '_full.tif');
imageFile = [Folder file];
imageData = imread(strcat('C:\Users\student\Desktop\PC Lab\Day1\', imageFile));
[r, c, z] = size(imageData);
x = round(linspace(1,r,10));
y = round(linspace(1,c,10));
%imshow(strcat('Z:\Michaela Rikard\Kuba image resizes\', imageFile))

index = 1;
for i = 1:length(x)-1
    for j = 1:length(y)-1
        obj = imageData(x(i):x(i+1), y(j):y(j+1), :);
        %FileName = sprintf('s2_full_Tiles/tile_%d.tif', index);
        %FileName = sprintf(strcat(destination,'/tile_%d.tif'), index)
        %ImageFileName = sprintf('/tile_%d.tif', index);
        %FileName = strcat(Folder, ImageFileName);
        %imwrite(obj, FileName);
        subplot(9,9,index), imshow(obj)
        index = index + 1;
    end
end

for i = 1:81
    ImageFileName = sprintf('/tile_%d.tif', i);
    FileName = strcat(Folder, ImageFileName);
    subplot(9,9,i), imshow([FileName]);
end

disp('done')