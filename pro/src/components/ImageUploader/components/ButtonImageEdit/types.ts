export interface CropParams {
  xCropPercent: number
  yCropPercent: number
  heightCropPercent: number
  widthCropPercent: number
}

export interface UploadImageValues {
  draftImage?: File
  imageUrl?: string
  originalImageUrl?: string
  credit?: string
  cropParams?: CropParams
}
