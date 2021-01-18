import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { IMPORT_TAB_ID } from 'components/pages/Offer/Offer/Thumbnail/_constants'
import { ReactComponent as CloseModalIcon } from 'components/pages/Offer/Offer/Thumbnail/assets/close-modal.svg'
import Credit from 'components/pages/Offer/Offer/Thumbnail/Credit/Credit'
import ImportFromComputer from 'components/pages/Offer/Offer/Thumbnail/ImportFromComputer/ImportFromComputer'
import ImportFromURL from 'components/pages/Offer/Offer/Thumbnail/ImportFromURL/ImportFromURL'
import ImportTab from 'components/pages/Offer/Offer/Thumbnail/ImportTab/ImportTab'

const ThumbnailDialog = ({ setIsModalOpened }) => {
  const DIALOG_LABEL_ID = 'label_for_aria'

  const [tabId, setTabId] = useState(IMPORT_TAB_ID)
  const [activeTab, setActiveTab] = useState(IMPORT_TAB_ID)
  // eslint-disable-next-line no-unused-vars
  const [thumbnail, setThumbnail] = useState({})
  // eslint-disable-next-line no-unused-vars
  const [credit, setCredit] = useState('')
  const [step, setStep] = useState(1)

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  const changeTab = useCallback(
    tabId => () => {
      setTabId(tabId)
      setActiveTab(tabId)
    },
    []
  )

  return (
    <DialogBox
      extraClassNames={step === 1 ? 'thumbnail-dialog tnd-step1' : 'thumbnail-dialog'}
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={closeModal}
    >
      <header>
        <h1
          className="tnd-header"
          id={DIALOG_LABEL_ID}
        >
          {'Ajouter une image'}
        </h1>
      </header>
      <>
        {step === 1 && (
          <>
            <ImportTab
              activeTab={activeTab}
              changeTab={changeTab}
            />
            {tabId === IMPORT_TAB_ID ? (
              <ImportFromComputer
                setStep={setStep}
                setThumbnail={setThumbnail}
              />
            ) : (
              <ImportFromURL />
            )}
            <hr className="tnd-hr" />
          </>
        )}
        {step === 2 && (
          <Credit
            setCredit={setCredit}
            setStep={setStep}
          />
        )}
      </>
      <button
        className="tnd-close"
        onClick={closeModal}
        title="Fermer la modale"
        type="button"
      >
        <CloseModalIcon />
      </button>
    </DialogBox>
  )
}

ThumbnailDialog.propTypes = {
  setIsModalOpened: PropTypes.func.isRequired,
}

export default ThumbnailDialog
