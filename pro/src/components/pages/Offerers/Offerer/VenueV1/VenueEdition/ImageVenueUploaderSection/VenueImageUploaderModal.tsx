import React, { FunctionComponent } from 'react'

import { imageConstraints } from 'new_components/ConstraintCheck/imageConstraints'
import DialogBox from 'new_components/DialogBox'

import { ImportFromComputer } from '../ImportFromComputer/ImportFromComputer'

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
}) => (
  <DialogBox
    hasCloseButton
    labelledBy="Ajouter une image"
    onDismiss={onDismiss}
  >
    <ImportFromComputer
      constraints={constraints}
      imageTypes={IMAGE_TYPES}
      onSetImage={alert}
      orientation="landscape"
    />
  </DialogBox>
)
