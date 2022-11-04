// croppingRect give us the top left corner of the cropped area
// where AvatarEditor expect the center of it
export const coordonateToPosition = (coordonate: number, size: number) =>
  coordonate + size / 2

// height_crop_percent of croppingRect is the ratio of the cropped image height
// compare to the original image height which corresponds to the inverse of the zoom scale
export const heightCropPercentToScale = (heightCropPercent: number) =>
  1 / heightCropPercent
