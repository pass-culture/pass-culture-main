import * as yup from 'yup'

import { getImageBitmap } from 'utils/image'

import { OrientationEnum } from './types'

export interface IGetValidationSchemaArgs {
  types?: string[]
  minWidth?: number
  maxSize?: number
  minRatio?: number
  minHeight?: number
  orientation: OrientationEnum
}

const getValidationSchema = ({
  maxSize,
  minWidth,
  types,
  minRatio,
  minHeight,
  orientation,
}: IGetValidationSchemaArgs) => {
  const validationSchema: {
    size?: yup.AnySchema
    format?: yup.AnySchema
    width?: yup.AnySchema
    height?: yup.AnySchema
    minRatio?: yup.AnySchema
  } = {}

  /* istanbul ignore next: DEBT, TO FIX */
  if (maxSize) {
    const displayedMaxSize = maxSize / 1000000
    validationSchema.size = yup.mixed().test({
      message: `Poids maximal du fichier : ${displayedMaxSize} Mo`,
      test: (_size, context: yup.TestContext) => {
        return context.parent.image.size < maxSize
      },
    })
  }

  /* istanbul ignore next: DEBT, TO FIX */
  if (types) {
    const displayedFileTypes = types
      .map((fileType: string) => fileType.split('/')[1].toUpperCase())
      .join(', ')
    validationSchema.format = yup.mixed().test({
      message: `Formats supportés: ${displayedFileTypes}`,
      test: (_type, context: yup.TestContext) => {
        const isValid = types.includes(context.parent.image.type)
        return isValid
      },
    })
  }

  /* istanbul ignore next: DEBT, TO FIX */
  if (minWidth) {
    validationSchema.width = yup.mixed().test({
      message: `Largeur minimale de l’image : ${minWidth} px`,
      test: async (_width, context: yup.TestContext) => {
        const imageBitmap = await getImageBitmap(context.parent.image)
        return imageBitmap !== null && imageBitmap.width >= minWidth
      },
    })
  }

  if (minHeight) {
    validationSchema.height = yup.mixed().test({
      message: `La hauteur minimale de l’image : ${minHeight} px`,
      test: async (_height, context: yup.TestContext) => {
        const imageBitmap = await getImageBitmap(context.parent.image)
        return imageBitmap !== null && imageBitmap.height >= minHeight
      },
    })
  }

  if (minRatio) {
    validationSchema.minRatio = yup.mixed().test({
      test: async (_width, context: yup.TestContext) => {
        const imageBitmap = await getImageBitmap(context.parent.image)
        if (imageBitmap === null) {
          return true
        }

        // if the ratio is +- 0.4, then the image needs to be higher
        // If it's -= 0.4 the image is too small, so we only check ratio + tooClose value
        const tooCloseNumber = 0.4
        const totalMinRatio = minRatio + tooCloseNumber
        const imageRatio = {
          [OrientationEnum.LANDSCAPE]:
            (imageBitmap.height / imageBitmap.width) * 100,
          [OrientationEnum.PORTRAIT]:
            (imageBitmap.width / imageBitmap.height) * 100,
        }[orientation]

        return imageRatio >= totalMinRatio
      },
    })
  }

  return yup.object().shape(validationSchema)
}

export default getValidationSchema
