export interface CropParams {
  xCropPercent: number
  yCropPercent: number
  heightCropPercent: number
  widthCropPercent: number
}

export interface UploadImageValues {
  imageUrl?: string
  originalImageUrl?: string
  credit?: string
  cropParams?: CropParams
}
