import React, { useCallback, useState, FunctionComponent } from 'react'
import { CroppedRect } from 'react-avatar-editor'

import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import DialogBox from 'new_components/DialogBox'
import { ImagePreview } from 'new_components/ImagePreview/ImagePreview'
import { ImagePreviewMode } from 'new_components/ImagePreview/types'

import { ImportFromComputer } from '../ImportFromComputer/ImportFromComputer'
import { VenueImageEdit } from '../VenueImageEdit/VenueImageEdit'

import { IMAGE_TYPES, MAX_IMAGE_SIZE, MIN_IMAGE_WIDTH } from './constants'

type Props = {
  onDismiss: () => void
}

const constraints = [
  imageConstraints.landscape(),
  imageConstraints.formats(IMAGE_TYPES),
  imageConstraints.size(MAX_IMAGE_SIZE),
  imageConstraints.width(MIN_IMAGE_WIDTH),
]

export const VenueImageUploaderModal: FunctionComponent<Props> = ({
  onDismiss,
}) => {
  const [image, setImage] = useState<File>()
  const [credit, setCredit] = useState('')
  const [croppingRect, setCroppingRect] = useState<CroppedRect>()
  const [editedImage, setEditedImage] = useState('')

  const onSetImage = useCallback(
    file => {
      return setImage(file)
    },
    [setImage]
  )

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
      ) : (
        <VenueImageEdit
          closeModal={onDismiss}
          credit={credit}
          image={image}
          onSetCredit={setCredit}
          setCroppingRect={setCroppingRect}
          setEditedImage={setEditedImage}
        />
      )}
    </DialogBox>
  )
}
