export interface CropParams {
  xCropPercent: number
  yCropPercent: number
  heightCropPercent: number
  widthCropPercent: number
}

export interface UploadImageValues {
  draftImage?: File
  croppedImageUrl?: string
  originalImageUrl?: string
  credit?: string
  cropParams?: CropParams
}

export enum UploaderModeEnum {
  OFFER = 'offer',
  OFFER_COLLECTIVE = 'offer_collective',
  VENUE = 'venue',
}
