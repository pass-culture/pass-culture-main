import React, { useCallback, useState } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import useNotification from 'components/hooks/useNotification'
import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import DialogBox from 'new_components/DialogBox'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { ImportFromComputer } from '../ImportFromComputer/ImportFromComputer'
import { VenueImageEdit } from '../VenueImageEdit/VenueImageEdit'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'

import { IMAGE_TYPES, MAX_IMAGE_SIZE, MIN_IMAGE_WIDTH } from './constants'
import { getDataURLFromImageURL } from './utils'

type VenueImageUploaderModalProps = {
  venueId: string
  onDismiss: () => void
  venueCredit: string
  onImageUpload: ({
    bannerUrl,
    credit,
  }: {
    bannerUrl: string
    credit: string
  }) => void
  defaultImage?: string
}

const constraints = [
  imageConstraints.formats(IMAGE_TYPES),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
]

export const VenueImageUploaderModal = ({
  venueId,
  onDismiss,
  defaultImage,
  venueCredit,
  onImageUpload,
}: VenueImageUploaderModalProps): JSX.Element => {
  const [image, setImage] = useState<string | undefined>(defaultImage)
  const [credit, setCredit] = useState(venueCredit)
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()
  const [editedImage, setEditedImage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const notification = useNotification()

  const onSetImage = useCallback(
    file => {
      setImage(file)
    },
    [setImage]
  )

  const onEditedImageSave = useCallback(
    (dataUrl, croppedRect) => {
      setEditedImage(dataUrl)
      setCroppingRect(croppedRect)
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
    if (typeof croppingRect === 'undefined') return
    if (typeof image === 'undefined') return

    // the request needs the dataURL of the image,
    // so we need to retrieve it if we only have the URL
    const imageDataURL =
      typeof image === 'string' ? await getDataURLFromImageURL(image) : image

    setIsUploading(true)
    const { bannerUrl } = await postImageToVenue({
      venueId,
      banner: imageDataURL,
      xCropPercent: croppingRect.x,
      yCropPercent: croppingRect.y,
      heightCropPercent: croppingRect.height,
      imageCredit: credit,
    })
    onImageUpload({ bannerUrl, credit })
    setIsUploading(false)
    onDismiss()
    notification.success('Vos modifications ont bien été prises en compte')
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
          onEditedImageSave={onEditedImageSave}
          onReplaceImage={onReplaceImage}
          onSetCredit={setCredit}
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
