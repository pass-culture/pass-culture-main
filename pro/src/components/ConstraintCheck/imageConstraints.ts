import { getImageBitmap } from 'utils/image'

type FileChecker = (file: File) => Promise<boolean>

export type Constraint = {
  id: string
  description: string
  asyncValidator: FileChecker
}

export const imageConstraints = {
  formats: (supportedImageTypes: string[]): Constraint => {
    const isNotAnImage: FileChecker = async (file) =>
      supportedImageTypes.includes(file.type) &&
      (await getImageBitmap(file)) !== null
    return {
      id: 'formats',
      description: 'Formats supportés : JPG, PNG',
      asyncValidator: isNotAnImage,
    }
  },
  size: (maxSize: number): Constraint => {
    const isTooBig: FileChecker = async (file) => file.size <= maxSize

    return {
      id: 'size',
      description: 'Poids maximal du fichier : 10 Mo',
      asyncValidator: isTooBig,
    }
  },
  width: (minWidth: number): Constraint => {
    const isOfPoorQuality: FileChecker = async (file) => {
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
    const isOfPoorQuality: FileChecker = async (file) => {
      if (!minHeight) {
        return false
      }
      const imageBitmap = await getImageBitmap(file)
      return imageBitmap !== null && imageBitmap.height >= minHeight
    }

    return {
      id: 'height',
      description: `Hauteur minimale de l’image : ${minHeight} px`,
      asyncValidator: isOfPoorQuality,
    }
  },
}

export const getValidatorErrors = async (
  constraints: Constraint[],
  file: File
): Promise<string[]> => {
  const failingConstraints = await Promise.all(
    constraints.map((contraint) =>
      contraint
        .asyncValidator(file)
        .then((isValid) => (isValid ? undefined : contraint.id))
    )
  )

  return failingConstraints.filter((maybeId): maybeId is string => !!maybeId)
}
