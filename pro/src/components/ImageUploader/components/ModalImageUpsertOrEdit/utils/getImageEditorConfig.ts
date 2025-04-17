import { UploaderModeEnum } from 'components/ImageUploader/types'

import { getCropMaxDimension } from './getCropMaxDimension'

export const getImageEditorConfig = (
  width: number,
  height: number,
  mode: UploaderModeEnum
) => {
  // FIXME: Do we still need this type of logic after
  // format image constraint withdrawal ?
  const minWidth = 400
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
      cropBorderColor: '#FFF',
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.OFFER_COLLECTIVE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 2) / 3,
      cropBorderColor: '#FFF',
      cropBorderHeight: 50,
      cropBorderWidth: 105,
      maxScale,
    },
    [UploaderModeEnum.VENUE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 3) / 2,
      cropBorderColor: '#FFF',
      cropBorderHeight: 40,
      cropBorderWidth: 100,
      maxScale,
    },
  }[mode]
}
