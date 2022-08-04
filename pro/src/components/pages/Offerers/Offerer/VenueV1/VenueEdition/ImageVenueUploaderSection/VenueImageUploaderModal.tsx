import React, { useCallback, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { getDataURLFromImageURL } from 'apiClient/helpers'
import useNotification from 'components/hooks/useNotification'
import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import DialogBox from 'new_components/DialogBox'
import {
  coordonateToPosition,
  heightCropPercentToScale,
} from 'new_components/ImageEditor/utils'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { ImportFromComputer } from '../ImportFromComputer/ImportFromComputer'
import { VenueImageEdit } from '../VenueImageEdit/VenueImageEdit'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'

import { IMAGE_TYPES, MAX_IMAGE_SIZE, MIN_IMAGE_WIDTH } from './constants'
import { IVenueBannerMetaProps } from './ImageVenueUploaderSection'

interface IVenueImageUploaderModalProps {
  venueId: string
  onDismiss: () => void
  onImageUpload: ({
    bannerUrl,
    bannerMeta,
  }: {
    bannerUrl: string
    bannerMeta: IVenueBannerMetaProps
  }) => void
  venueBanner?: IVenueBannerMetaProps
  venueImage?: string
}

const constraints = [
  imageConstraints.formats(IMAGE_TYPES),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
]

export const VenueImageUploaderModal = ({
  venueId,
  onDismiss,
  venueBanner,
  venueImage,
  onImageUpload,
}: IVenueImageUploaderModalProps): JSX.Element => {
  const [image, setImage] = useState<string | undefined>(
    venueBanner?.original_image_url
      ? venueBanner?.original_image_url
      : venueImage
  )
  const [credit, setCredit] = useState(venueBanner?.image_credit || '')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()
  const [editedImage, setEditedImage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  // First version of the back don't use width_crop_percent which is needed to display the original image with the correct crop
  const [editorInitialScale, setEditorInitialScale] = useState(
    venueBanner
      ? heightCropPercentToScale(venueBanner.crop_params.height_crop_percent)
      : 1
  )
  const [editorInitialPosition, setEditorInitialPosition] = useState({
    x: venueBanner
      ? coordonateToPosition(
          venueBanner.crop_params.x_crop_percent,
          venueBanner.crop_params.width_crop_percent
        )
      : 0.5,
    y: venueBanner
      ? coordonateToPosition(
          venueBanner.crop_params.y_crop_percent,
          venueBanner.crop_params.height_crop_percent
        )
      : 0.5,
  })
  const notification = useNotification()

  const onSetImage = useCallback(
    (file: string) => {
      setImage(file)
    },
    [setImage]
  )

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

  const onReplaceImage = useCallback(() => {
    setImage(undefined)
  }, [setImage])

  const onUpload = useCallback(async () => {
    if (typeof croppingRect === undefined) return
    if (typeof image === undefined) return

    try {
      setIsUploading(true)
      // the request needs the dataURL of the image,
      // so we need to retrieve it if we only have the URL
      const imageDataURL =
        typeof image === 'string' ? await getDataURLFromImageURL(image) : image
      const { bannerUrl, bannerMeta } = await postImageToVenue({
        venueId,
        banner: imageDataURL,
        xCropPercent: croppingRect?.x,
        yCropPercent: croppingRect?.y,
        heightCropPercent: croppingRect?.height,
        widthCropPercent: croppingRect?.width,
        imageCredit: credit,
      })
      onImageUpload({ bannerUrl, bannerMeta })
      setIsUploading(false)
      onDismiss()
      notification.success('Vos modifications ont bien été prises en compte')
    } catch {
      notification.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
      setIsUploading(false)
    }
  }, [
    venueId,
    image,
    croppingRect,
    onDismiss,
    notification,
    credit,
    onImageUpload,
  ])

  return (
    <DialogBox
      hasCloseButton
      labelledBy="Ajouter une image"
      onDismiss={onDismiss}
    >
      {!image ? (
        <ImportFromComputer
          constraints={constraints}
          imageTypes={IMAGE_TYPES}
          onSetImage={onSetImage}
          orientation="landscape"
        />
      ) : !croppingRect || !editedImage ? (
        <VenueImageEdit
          credit={credit}
          image={image}
          initialPosition={editorInitialPosition}
          initialScale={editorInitialScale}
          onEditedImageSave={onEditedImageSave}
          onReplaceImage={onReplaceImage}
          onSetCredit={setCredit}
          saveInitialPosition={setEditorInitialPosition}
          saveInitialScale={setEditorInitialScale}
        />
      ) : (
        <VenueImagePreview
          isUploading={isUploading}
          onGoBack={navigateFromPreviewToEdit}
          onUploadImage={onUpload}
          preview={editedImage}
          withActions
        />
      )}
    </DialogBox>
  )
}
