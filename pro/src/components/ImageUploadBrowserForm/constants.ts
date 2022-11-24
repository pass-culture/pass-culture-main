import { UploaderModeEnum } from 'components/ImageUploader/types'

import { OrientationEnum } from './types'

export const modeValidationConstraints = {
  [UploaderModeEnum.OFFER]: {
    maxSize: 10000000,
    minWidth: 400,
    types: ['image/png', 'image/jpeg'],
    minRatio: 6 / 9,
    minHeight: 400,
    orientation: OrientationEnum.PORTRAIT,
  },
  [UploaderModeEnum.OFFER_COLLECTIVE]: {
    maxSize: 10000000,
    minWidth: 400,
    types: ['image/png', 'image/jpeg'],
    minRatio: 6 / 9,
    minHeight: 400,
    orientation: OrientationEnum.PORTRAIT,
  },
  [UploaderModeEnum.VENUE]: {
    maxSize: 10000000,
    minWidth: 600,
    types: ['image/png', 'image/jpeg'],
    minRatio: 3 / 2,
    orientation: OrientationEnum.LANDSCAPE,
  },
}
