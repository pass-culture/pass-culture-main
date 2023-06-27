import React, { useCallback, useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getFileFromURL } from 'apiClient/helpers'
import DialogBox from 'components/DialogBox'
import {
  coordonateToPosition,
  heightCropPercentToScale,
} from 'components/ImageEditor/utils'
import { ImageUploadBrowserFormValues } from 'components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { UploadImageValues } from '../types'

import { ModalImageCrop } from './ModalImageCrop'
import { ModalImageUploadBrowser } from './ModalImageUploadBrowser'
import { ModalImageUploadConfirm } from './ModalImageUploadConfirm'

export interface OnImageUploadArgs {
  imageFile: File
  imageCroppedDataUrl?: string
  credit: string | null
  cropParams?: CroppedRect
}

interface ModalImageEditProps {
  mode: UploaderModeEnum
  onDismiss: () => void
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
  initialValues?: UploadImageValues
}
// FIXME: find a way to test FileReader
/* istanbul ignore next: DEBT, TO FIX */
const ModalImageEdit = ({
  mode,
  onDismiss,
  onImageUpload,
  initialValues = {},
}: ModalImageEditProps): JSX.Element | null => {
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
      setImage(await getFileFromURL(url))
      setIsReady(true)
    }
    const imageUrl = initialOriginalImageUrl
      ? initialOriginalImageUrl
      : initialImageUrl
    imageUrl ? setImageFromUrl(imageUrl) : setIsReady(true)
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
  const [editorInitialScale, setEditorInitialScale] = useState(
    initalHeightCropPercent
      ? heightCropPercentToScale(initalHeightCropPercent)
      : 1
  )
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

  const navigateFromPreviewToEdit = useCallback(() => {
    setEditedImageDataUrl('')
  }, [])

  const onImageClientUpload = (values: ImageUploadBrowserFormValues) => {
    setImage(values.image || undefined)
  }

  const onReplaceImage = useCallback(() => {
    setImage(undefined)
  }, [setImage])

  const handleOnUpload = async (
    croppedRect?: CroppedRect,
    imageToUpload?: File,
    imageDataUrl?: string
  ) => {
    if (croppedRect === undefined || imageToUpload === undefined) {
      return
    }

    await onImageUpload({
      imageFile: imageToUpload,
      imageCroppedDataUrl: imageDataUrl,
      cropParams: croppedRect,
      credit,
    })
    onDismiss()
    setIsUploading(false)
  }

  const showPreviewInModal = mode !== UploaderModeEnum.OFFER_COLLECTIVE

  const onEditedImageSave = useCallback(
    (dataUrl: string, croppedRect: CroppedRect) => {
      setCroppingRect(croppedRect)
      setEditedImageDataUrl(dataUrl)

      if (!showPreviewInModal) {
        handleOnUpload(croppedRect, image, dataUrl)
      }
    },
    [
      setEditedImageDataUrl,
      setCroppingRect,
      showPreviewInModal,
      handleOnUpload,
      image,
    ]
  )

  if (!isReady) {
    return null
  }

  return (
    <DialogBox
      hasCloseButton
      labelledBy="Ajouter une image"
      onDismiss={onDismiss}
    >
      {!image ? (
        <ModalImageUploadBrowser
          onImageClientUpload={onImageClientUpload}
          mode={mode}
        />
      ) : !croppingRect || !editedImageDataUrl ? (
        <ModalImageCrop
          credit={credit}
          image={image}
          initialPosition={editorInitialPosition}
          initialScale={editorInitialScale}
          onEditedImageSave={onEditedImageSave}
          onReplaceImage={onReplaceImage}
          onSetCredit={setCredit}
          saveInitialPosition={setEditorInitialPosition}
          saveInitialScale={setEditorInitialScale}
          mode={mode}
          submitButtonText={showPreviewInModal ? 'Suivant' : 'Enregistrer'}
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
      )}
    </DialogBox>
  )
}

export default ModalImageEdit
