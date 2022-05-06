filenames = string.empty();
for i = 1:81
    f = sprintf('C:/Users/student/Desktop/PC Lab/Day6/ED2_Mask_3/tile_%d',i) %Directory for binary images
    f = strcat(f,'_mask.tif')
    filenames(i) = f;
end
cd 'C:/Users/student/Desktop/PC Lab/Data3'
ilastik = imtile(filenames,'GridSize',[9 9]);
imwrite(ilastik,'ED2_d6.tif');

