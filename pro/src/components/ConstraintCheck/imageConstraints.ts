import { OrientationEnum } from 'components/ImageUploadBrowserForm/types'
import { getImageBitmap } from 'utils/image'

type FileChecker = (file: File) => Promise<boolean>

export type Constraint = {
  id: string
  description: string
  asyncValidator: FileChecker
  hideDescription?: boolean
}

export const imageConstraints = {
  formats: (supportedImageTypes: string[]): Constraint => {
    const isNotAnImage: FileChecker = async file =>
      supportedImageTypes.includes(file.type) &&
      (await getImageBitmap(file)) !== null
    return {
      id: 'formats',
      description: 'Formats supportés : JPG, PNG',
      asyncValidator: isNotAnImage,
    }
  },
  size: (maxSize: number): Constraint => {
    const isTooBig: FileChecker = async file => file.size <= maxSize

    return {
      id: 'size',
      description: 'Poids maximal du fichier : 10 Mo',
      asyncValidator: isTooBig,
    }
  },
  width: (minWidth: number): Constraint => {
    const isOfPoorQuality: FileChecker = async file => {
      const imageBitmap = await getImageBitmap(file)
      return imageBitmap !== null && imageBitmap.width >= minWidth
    }

    return {
      id: 'width',
      description: `Largeur minimale de l’image : ${minWidth} px`,
      asyncValidator: isOfPoorQuality,
    }
  },
  height: (minHeight?: number): Constraint => {
    const isOfPoorQuality: FileChecker = async file => {
      if (!minHeight) {
        return false
      }
      const imageBitmap = await getImageBitmap(file)
      return imageBitmap !== null && imageBitmap.height >= minHeight
    }

    return {
      id: 'height',
      description: `La hauteur minimale de l’image : ${minHeight} px`,
      asyncValidator: isOfPoorQuality,
      hideDescription: !minHeight || minHeight <= 0,
    }
  },
  minRatio: (minRatio: number, orientation: OrientationEnum): Constraint => {
    const isRatioTooClose: FileChecker = async file => {
      const imageBitmap = await getImageBitmap(file)
      // istanbul ignore next
      // return true because we don't want to display the message if no image
      if (imageBitmap === null) {
        return true
      }

      // if the ratio is +- 0.4, then the image needs to be higher
      // If it's -= 0.4 the image is too small, so we only check ratio + tooClose value
      const tooCloseNumber = 0.4
      const totalMinRatio = minRatio + tooCloseNumber
      const imageRatio = {
        [OrientationEnum.LANDSCAPE]:
          (imageBitmap.width / imageBitmap.height) * 100,
        [OrientationEnum.PORTRAIT]:
          (imageBitmap.width / imageBitmap.height) * 100,
      }[orientation]

      return imageRatio >= totalMinRatio
    }

    return {
      id: 'minRatio',
      description: `La hauteur de l'image n'est pas assez grande.`,
      asyncValidator: isRatioTooClose,
      hideDescription: true,
    }
  },
}

export const getValidatorErrors = async (
  constraints: Constraint[],
  file: File
): Promise<string[]> => {
  const failingConstraints = await Promise.all(
    constraints.map(contraint =>
      contraint
        .asyncValidator(file)
        .then(isValid => (isValid ? undefined : contraint.id))
    )
  )

  return failingConstraints.filter((maybeId): maybeId is string => !!maybeId)
}
