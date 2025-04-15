import { useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import { useNotification } from 'commons/hooks/useNotification'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { UploadImageValues } from '../ButtonImageEdit/types'

import {
  coordonateToPosition,
  widthCropPercentToScale,
} from './components/ModalImageCrop/ImageEditor/utils'
import { ModalImageCrop } from './components/ModalImageCrop/ModalImageCrop'
import { ImageUploadBrowserFormValues } from './components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'
import { ModalImageUploadBrowser } from './components/ModalImageUploadBrowser/ModalImageUploadBrowser'

export interface OnImageUploadArgs {
  imageFile: File
  imageCroppedDataUrl?: string
  cropParams?: CroppedRect
  credit: string | null
}

interface ModalImageEditProps {
  mode: UploaderModeEnum
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete?: () => void
  initialValues?: UploadImageValues
}

// TODO: find a way to test FileReader
/* istanbul ignore next: DEBT, TO FIX */
export const ModalImageEdit = ({
  mode,
  onImageUpload,
  onImageDelete,
  initialValues = {},
}: ModalImageEditProps): JSX.Element | null => {
  const notification = useNotification()
  const [isReady, setIsReady] = useState<boolean>(false)

  const {
    draftImage,
    imageUrl: initialImageUrl,
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = initialValues

  const [image, setImage] = useState<File | undefined>(draftImage)

  const imageUrl = initialOriginalImageUrl
    ? initialOriginalImageUrl
    : initialImageUrl

  useEffect(() => {
    async function setImageFromUrl(url: string) {
      try {
        setImage(await getFileFromURL(url))
      } catch {
        notification.error('Erreur lors de la récupération de votre image.')
      }
    }

    if (imageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(imageUrl)
    }
    setIsReady(true)
  }, [])

  // First version of the back don't use width_crop_percent which is needed to display the original image with the correct crop
  const {
    xCropPercent: initalXCropPercent,
    yCropPercent: initalYCropPercent,
    heightCropPercent: initalHeightCropPercent,
    widthCropPercent: initalWidthCropPercent,
  } = initialCropParams || {}

  const [editorInitialPosition, setEditorInitialPosition] = useState({
    x:
      initalXCropPercent && initalWidthCropPercent
        ? coordonateToPosition(initalXCropPercent, initalWidthCropPercent)
        : 0.5,
    y:
      initalYCropPercent && initalHeightCropPercent
        ? coordonateToPosition(initalYCropPercent, initalHeightCropPercent)
        : 0.5,
  })

  const onImageClientUpload = (values: ImageUploadBrowserFormValues) => {
    setImage(values.image || undefined)
  }

  const onReplaceImage = () => {
    setImage(undefined)
  }

  const handleImageDelete = () => {
    if (!initialImageUrl && !initialOriginalImageUrl) {
      setImage(undefined)
    } else {
      onImageDelete?.()
    }
  }

  const onEditedImageSave = (
    credit: string | null,
    imageDataUrl?: string,
    croppedRect?: CroppedRect
  ) => {
    if (croppedRect === undefined || image === undefined) {
      return
    }

    onImageUpload({
      imageFile: image,
      imageCroppedDataUrl: imageDataUrl,
      cropParams: croppedRect,
      credit: credit,
    })
  }

  return !image ? (
    <ModalImageUploadBrowser
      onImageClientUpload={onImageClientUpload}
      mode={mode}
      isReady={isReady}
    />
  ) : (
    <ModalImageCrop
      initialCredit={initialCredit}
      image={image}
      initialPosition={editorInitialPosition}
      initialScale={
        initalWidthCropPercent
          ? widthCropPercentToScale(initalWidthCropPercent)
          : 1
      }
      onEditedImageSave={onEditedImageSave}
      onReplaceImage={onReplaceImage}
      onImageDelete={handleImageDelete}
      saveInitialPosition={setEditorInitialPosition}
      mode={mode}
      imageUrl={initialImageUrl}
    />
  )
}
