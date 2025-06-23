import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'

import { getCropMaxDimension } from './getCropMaxDimension'

export const getImageEditorConfig = (
  width: number,
  height: number,
  mode: UploaderModeEnum
) => {
  const minWidth: number = {
    [UploaderModeEnum.OFFER]: 400,
    [UploaderModeEnum.OFFER_COLLECTIVE]: 400,
    [UploaderModeEnum.VENUE]: 600,
  }[mode]

  const { width: maxWidth } = getCropMaxDimension({
    originalDimensions: { width, height },
    orientation: mode === UploaderModeEnum.VENUE ? 'landscape' : 'portrait',
  })
  const maxScale: number = Math.min(4, (maxWidth - 10) / minWidth)

  const canvasHeight: number = {
    [UploaderModeEnum.OFFER]: 297,
    [UploaderModeEnum.OFFER_COLLECTIVE]: 297,
    [UploaderModeEnum.VENUE]: 138,
  }[mode]

  return {
    [UploaderModeEnum.OFFER]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 2) / 3,
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.OFFER_COLLECTIVE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 2) / 3,
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.VENUE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 3) / 2,
      cropBorderHeight: 40,
      cropBorderWidth: 100,
      maxScale,
    },
  }[mode]
}
