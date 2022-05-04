type FileChecker = (file: File) => Promise<boolean>

export type Constraint = {
  id: string
  description: string
  asyncValidator: FileChecker
}

const getImageBitmap = async (file: File): Promise<ImageBitmap | null> => {
  // Polyfill for Safari and IE not supporting createImageBitmap
  if (!('createImageBitmap' in window)) {
    window.createImageBitmap = async (
      blob: ImageBitmapSource
    ): Promise<ImageBitmap> =>
      new Promise(resolve => {
        const img = document.createElement('img')
        img.addEventListener('load', function () {
          // eslint-disable-next-line
          resolve(this as any)
        })
        img.src = URL.createObjectURL(blob as Blob)
      })
  }
  return await createImageBitmap(file).catch(() => null)
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
