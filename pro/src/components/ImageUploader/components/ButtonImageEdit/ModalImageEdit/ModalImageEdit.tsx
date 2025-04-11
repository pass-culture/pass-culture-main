import { useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import { useNotification } from 'commons/hooks/useNotification'
import {
  coordonateToPosition,
  widthCropPercentToScale,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/utils'
import { ImageUploadBrowserFormValues } from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { UploadImageValues } from '../types'

import { ModalImageCrop } from './components/ModalImageCrop/ModalImageCrop'
import { ModalImageUploadBrowser } from './components/ModalImageUploadBrowser/ModalImageUploadBrowser'
import { ModalImageUploadConfirm } from './components/ModalImageUploadConfirm/ModalImageUploadConfirm'

export interface OnImageUploadArgs {
  imageFile: File
  imageCroppedDataUrl?: string
  credit: string | null
  cropParams?: CroppedRect
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
    imageUrl: initialImageUrl,
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = initialValues

  const [image, setImage] = useState<File | undefined>()
  useEffect(() => {
    async function setImageFromUrl(url: string) {
      try {
        setImage(await getFileFromURL(url))
      } catch {
        notification.error('Erreur lors de la récupération de votre image.')
      }
    }

    const imageUrl = initialOriginalImageUrl
      ? initialOriginalImageUrl
      : initialImageUrl
    if (imageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(imageUrl)
    }
    setIsReady(true)
  }, [])

  const [credit, setCredit] = useState(initialCredit || '')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()

  const [editedImageDataUrl, setEditedImageDataUrl] = useState('')
  const [isUploading, setIsUploading] = useState(false)

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

  const navigateFromPreviewToEdit = () => {
    setEditedImageDataUrl('')
  }

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

  const handleOnUpload = (
    croppedRect?: CroppedRect,
    imageToUpload?: File,
    imageDataUrl?: string
  ) => {
    if (croppedRect === undefined || imageToUpload === undefined) {
      return
    }

    onImageUpload({
      imageFile: imageToUpload,
      imageCroppedDataUrl: imageDataUrl,
      cropParams: croppedRect,
      credit,
    })
    setIsUploading(false)
  }

  const onEditedImageSave = (dataUrl: string, croppedRect: CroppedRect) => {
    setCroppingRect(croppedRect)
    setEditedImageDataUrl(dataUrl)

    handleOnUpload(croppedRect, image, dataUrl)
  }

  return !image ? (
    <ModalImageUploadBrowser
      onImageClientUpload={onImageClientUpload}
      mode={mode}
      isReady={isReady}
    />
  ) : !croppingRect || !editedImageDataUrl ? (
    <ModalImageCrop
      credit={credit}
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
      onSetCredit={setCredit}
      saveInitialPosition={setEditorInitialPosition}
      mode={mode}
      showPreviewInModal={false}
    />
  ) : (
    <ModalImageUploadConfirm
      isUploading={isUploading}
      onGoBack={navigateFromPreviewToEdit}
      onUploadImage={() =>
        handleOnUpload(croppingRect, image, editedImageDataUrl)
      }
      imageUrl={editedImageDataUrl}
      mode={mode}
    />
  )
}
