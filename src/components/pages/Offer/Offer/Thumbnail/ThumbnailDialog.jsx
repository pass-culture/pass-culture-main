import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { ReactComponent as CloseModalIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/close-modal.svg'

const ThumbnailDialog = ({ setIsModalOpened }) => {
  const DIALOG_LABEL_ID = 'label_for_aria'

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  return (
    <DialogBox
      extraClassNames="thumbnail-dialog"
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={closeModal}
    >
      <button
        className="tbd-close"
        onClick={closeModal}
        title="Fermer la modale"
        type="button"
      >
        <CloseModalIcon />
      </button>
      <header className="tbd-header">
        <h1 id={DIALOG_LABEL_ID}>
          {'Ajouter une image'}
        </h1>
      </header>
    </DialogBox>
  )
}

ThumbnailDialog.propTypes = {
  setIsModalOpened: PropTypes.func.isRequired,
}

export default ThumbnailDialog
