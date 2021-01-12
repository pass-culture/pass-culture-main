import PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { IMPORT_TAB_ID } from 'components/pages/Offer/Offer/Thumbnail/_constants'
import { ReactComponent as CloseModalIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/close-modal.svg'
import ImportFromComputer from 'components/pages/Offer/Offer/Thumbnail/ImportFromComputer/ImportFromComputer'
import ImportFromURL from 'components/pages/Offer/Offer/Thumbnail/ImportFromURL/ImportFromURL'
import ImportTab from 'components/pages/Offer/Offer/Thumbnail/ImportTab/ImportTab'

const ThumbnailDialog = ({ setIsModalOpened }) => {
  const fileInputRef = useRef()
  const DIALOG_LABEL_ID = 'label_for_aria'

  const [tabId, setTabId] = useState(IMPORT_TAB_ID)
  const [activeStep, setActiveStep] = useState(IMPORT_TAB_ID)

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  const changeTab = useCallback(
    tabId => () => {
      setTabId(tabId)
      setActiveStep(tabId)
    },
    []
  )

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
      <ImportTab
        activeStep={activeStep}
        changeTab={changeTab}
        ref={fileInputRef}
      />
      {tabId === IMPORT_TAB_ID ? <ImportFromComputer /> : <ImportFromURL />}
      <hr className="tnd-hr" />
    </DialogBox>
  )
}

ThumbnailDialog.propTypes = {
  setIsModalOpened: PropTypes.func.isRequired,
}

export default ThumbnailDialog
