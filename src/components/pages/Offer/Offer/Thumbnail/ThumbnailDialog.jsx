import PropTypes from 'prop-types'
import React, { useCallback, useRef } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { ReactComponent as CloseModalIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/close-modal.svg'
import ThumbnailBreadcrumb from 'components/pages/Offer/Offer/Thumbnail/ThumbnailBreadcrumb/ThumbnailBreadcrumb'
import ThumbnailFile from 'components/pages/Offer/Offer/Thumbnail/ThumbnailFile/ThumbnailFile'

const ThumbnailDialog = ({ setIsModalOpened }) => {
  const fileInputRef = useRef()
  const DIALOG_LABEL_ID = 'label_for_aria'

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  return (
    <DialogBox
      extraClassNames="thumbnail-dialog"
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={closeModal}
      ref={fileInputRef}
    >
      <button
        className="tnd-close"
        onClick={closeModal}
        title="Fermer la modale"
        type="button"
      >
        <CloseModalIcon />
      </button>
      <header>
        <h1
          className="tnd-header"
          id={DIALOG_LABEL_ID}
        >
          {'Ajouter une image'}
        </h1>
      </header>
      <ThumbnailBreadcrumb />
      <ThumbnailFile ref={fileInputRef} />
      <hr className="tnd-hr" />
    </DialogBox>
  )
}

ThumbnailDialog.propTypes = {
  setIsModalOpened: PropTypes.func.isRequired,
}

export default ThumbnailDialog
