import React, { useCallback, useEffect, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getDataURLFromImageURL } from 'apiClient/helpers'
import useNotification from 'components/hooks/useNotification'
import DialogBox from 'new_components/DialogBox'
import {
  coordonateToPosition,
  heightCropPercentToScale,
} from 'new_components/ImageEditor/utils'
import { IImageUploadBrowserFormValues } from 'new_components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'

import { IUploadImageValues } from '../types'

import { ModalImageCrop } from './ModalImageCrop'
import { ModalImageUploadBrowser } from './ModalImageUploadBrowser'
import { ModalImageUploadConfirm } from './ModalImageUploadConfirm'

export interface IOnImageUploadArgs {
  imageData: File
  credit: string
  cropParams?: CroppedRect
}

interface IModalImageEditProps {
  mode: UploaderModeEnum
  onDismiss: () => void
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  initialValues?: IUploadImageValues
}
const ModalImageEdit = ({
  mode,
  onDismiss,
  onImageUpload,
  initialValues = {},
}: IModalImageEditProps): JSX.Element | null => {
  const notify = useNotification()
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
      setImage(await getDataURLFromImageURL(url))
      setIsReady(true)
    }
    const imageUrl = initialOriginalImageUrl
      ? initialOriginalImageUrl
      : initialImageUrl
    imageUrl ? setImageFromUrl(imageUrl) : setIsReady(true)
  }, [])

  const [credit, setCredit] = useState(initialCredit || '')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()

  const [editedImage, setEditedImage] = useState('')
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

  const onEditedImageSave = useCallback(
    (dataUrl: string, croppedRect: CroppedRect) => {
      setCroppingRect(croppedRect)
      setEditedImage(dataUrl)
    },
    [setEditedImage, setCroppingRect]
  )

  const navigateFromPreviewToEdit = useCallback(() => {
    setEditedImage('')
  }, [])

  const onImageClientUpload = (values: IImageUploadBrowserFormValues) => {
    setImage(values.image || undefined)
  }

  const onReplaceImage = useCallback(() => {
    setImage(undefined)
  }, [setImage])

  const handleOnUpload = async () => {
    if (croppingRect === undefined) return
    if (image === undefined) return

    setIsUploading(true)
    const imageDataURL =
      typeof image === 'string' ? await getDataURLFromImageURL(image) : image

    await onImageUpload({
      imageData: imageDataURL,
      cropParams: croppingRect,
      credit,
    })
      .then(() => {
        notify.success('Vos modifications ont bien été prises en compte')
        onDismiss()
      })
      .catch(() => {
        notify.error(
          'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
        )
      })
    setIsUploading(false)
  }

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
      ) : !croppingRect || !editedImage ? (
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
        />
      ) : (
        <ModalImageUploadConfirm
          isUploading={isUploading}
          onGoBack={navigateFromPreviewToEdit}
          onUploadImage={handleOnUpload}
          imageUrl={editedImage}
          mode={mode}
        />
      )}
    </DialogBox>
  )
}

export default ModalImageEdit
