export interface IImageCropParams {
  xCropPercent: number
  yCropPercent: number
  heightCropPercent: number
  widthCropPercent: number
}

export interface IUploadImageValues {
  imageUrl?: string
  originalImageUrl?: string
  credit?: string
  cropParams?: IImageCropParams
}
