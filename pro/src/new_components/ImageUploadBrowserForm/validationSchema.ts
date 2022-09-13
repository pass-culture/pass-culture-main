import * as yup from 'yup'

const getImageBitmap = async (file: File): Promise<ImageBitmap | null> => {
  // Polyfill for Safari and IE not supporting createImageBitmap
  if (!('createImageBitmap' in window)) {
    window.createImageBitmap = async (
      blob: ImageBitmapSource
    ): Promise<ImageBitmap> =>
      new Promise(resolve => {
        const img = document.createElement('img')
        img.addEventListener('load', function () {
          resolve(this as any)
        })
        img.src = URL.createObjectURL(blob as Blob)
      })
  }
  return await createImageBitmap(file).catch(() => null)
}

export interface IGetValidationSchemaArgs {
  types?: string[]
  minWidth?: number
  maxSize?: number
}

const getValidationSchema = ({
  maxSize,
  minWidth,
  types,
}: IGetValidationSchemaArgs) => {
  const validationSchema: {
    size?: yup.AnySchema
    format?: yup.AnySchema
    width?: yup.AnySchema
  } = {}

  if (maxSize) {
    const displayedMaxSize = maxSize / 1000000
    validationSchema.size = yup.mixed().test({
      message: `Poids maximal du fichier : ${displayedMaxSize} Mo`,
      test: (_size, context: yup.TestContext) => {
        return context.parent.image.size < maxSize
      },
    })
  }

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

  if (minWidth) {
    validationSchema.width = yup.mixed().test({
      message: `Largeur minimale de l’image : ${minWidth} px`,
      test: async (_width, context: yup.TestContext) => {
        const imageBitmap = await getImageBitmap(context.parent.image)
        return imageBitmap !== null && imageBitmap.width >= minWidth
      },
    })
  }
  return yup.object().shape(validationSchema)
}

export default getValidationSchema
