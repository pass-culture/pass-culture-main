import { useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import { useNotification } from 'commons/hooks/useNotification'
import {
  coordonateToPosition,
  heightCropPercentToScale,
} from 'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageCrop/ImageEditor/utils'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { UploadImageValues } from '../types'

import { ModalImageCrop } from './components/ModalImageCrop/ModalImageCrop'

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
  imageFile: File | undefined
}

// TODO: find a way to test FileReader
/* istanbul ignore next: DEBT, TO FIX */
export const ModalImageEdit = ({
  mode,
  onImageUpload,
  onImageDelete,
  initialValues = {},
  imageFile,
}: ModalImageEditProps): JSX.Element | null => {
  const notification = useNotification()

  const {
    imageUrl: initialImageUrl,
    originalImageUrl: initialOriginalImageUrl,
    credit: initialCredit,
    cropParams: initialCropParams,
  } = initialValues

  const [image, setImage] = useState<File | undefined>(imageFile)

  useEffect(() => {
    async function setImageFromUrl(url: string) {
      try {
        setImage(await getFileFromURL(url))
      } catch {
        notification.error('Erreur lors de la récupération de votre imageTOTO.')
      }
    }

    const imageUrl = initialOriginalImageUrl
      ? initialOriginalImageUrl
      : initialImageUrl
    if (imageUrl) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setImageFromUrl(imageUrl)
    }
  }, [])

  const [credit, setCredit] = useState(initialCredit || '')

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
  }

  const onEditedImageSave = (dataUrl: string, croppedRect: CroppedRect) => {
    handleOnUpload(croppedRect, image, dataUrl)
  }

  return image ? (
    <ModalImageCrop
      credit={credit}
      image={image}
      initialPosition={editorInitialPosition}
      initialScale={
        initalHeightCropPercent
          ? heightCropPercentToScale(initalHeightCropPercent)
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
    <></>
  )
}
