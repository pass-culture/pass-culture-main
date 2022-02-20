import React, { FunctionComponent } from 'react'

import DialogBox from 'new_components/DialogBox'

import { VenueImageDelete } from '../VenueImageDelete/VenueImageDelete'

type Props = {
  onDismiss: () => void
  children?: never
}

export const VenueImageDeleteModal: FunctionComponent<Props> = ({
  onDismiss,
}) => {
  return (
    <DialogBox
      hasCloseButton
      labelledBy="Confirmer suppression"
      onDismiss={onDismiss}
    >
      <VenueImageDelete onCancel={onDismiss} />
    </DialogBox>
  )
}
