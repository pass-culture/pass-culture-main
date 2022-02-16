import React, { useCallback, useState, FunctionComponent } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import DialogBox from 'new_components/DialogBox'
import { postImageToVenue } from 'repository/pcapi/pcapi'

import { ImportFromComputer } from '../ImportFromComputer/ImportFromComputer'
import { VenueImageEdit } from '../VenueImageEdit/VenueImageEdit'
import { VenueImagePreview } from '../VenueImagePreview/VenueImagePreview'

import { IMAGE_TYPES, MAX_IMAGE_SIZE, MIN_IMAGE_WIDTH } from './constants'

type Props = {
  venueId: string
  onDismiss: () => void
  reloadImage: (url: string) => void
  defaultImage?: string
  children?: never
}

const constraints = [
  imageConstraints.formats(IMAGE_TYPES),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
]

export const VenueImageUploaderModal: FunctionComponent<Props> = ({
  venueId,
  onDismiss,
  reloadImage,
  defaultImage,
}) => {
  const [image, setImage] = useState<string | undefined>(defaultImage)
  const [credit, setCredit] = useState('')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()
  const [editedImage, setEditedImage] = useState('')
  const [isUploading, setIsUploading] = useState(false)

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

  const onUploadImage = useCallback(async () => {
    if (typeof croppingRect === 'undefined') return

    setIsUploading(true)
    const { bannerUrl } = await postImageToVenue({
      venueId,
      banner: image,
      xCropPercent: croppingRect.x,
      yCropPercent: croppingRect.y,
      heightCropPercent: croppingRect.height,
    })
    reloadImage(bannerUrl)
    setIsUploading(false)
    onDismiss()
  }, [venueId, image, croppingRect, reloadImage, onDismiss])

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
          closeModal={onDismiss}
          credit={credit}
          image={image}
          onEditedImageSave={onEditedImageSave}
          onSetCredit={setCredit}
        />
      ) : (
        <VenueImagePreview
          isUploading={isUploading}
          onGoBack={navigateFromPreviewToEdit}
          onUploadImage={onUploadImage}
          preview={editedImage}
        />
      )}
    </DialogBox>
  )
}
