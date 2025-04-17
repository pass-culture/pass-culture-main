// croppingRect give us the top left corner of the cropped area
// where AvatarEditor expect the center of it
export const coordonateToPosition = (coordonate: number, size: number) =>
  coordonate + size / 2

// width_crop_percent of croppingRect is the ratio of the cropped image width
export const widthCropPercentToScale = (widthCropPercent: number) =>
  100 / (widthCropPercent * 100)