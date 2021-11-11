/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { IMPORT_TAB_ID } from 'components/pages/Offers/Offer/Thumbnail/_constants'
import Advices from 'components/pages/Offers/Offer/Thumbnail/Advices/Advices'
import Credit from 'components/pages/Offers/Offer/Thumbnail/Credit/Credit'
import ImageEditorWrapper from 'components/pages/Offers/Offer/Thumbnail/ImageEditor/ImageEditorWrapper'
import ImportFromComputer from 'components/pages/Offers/Offer/Thumbnail/ImportFromComputer/ImportFromComputer'
import ImportFromURL from 'components/pages/Offers/Offer/Thumbnail/ImportFromURL/ImportFromURL'
import ImportTab from 'components/pages/Offers/Offer/Thumbnail/ImportTab/ImportTab'
import Preview from 'components/pages/Offers/Offer/Thumbnail/Preview/Preview'

const ThumbnailDialog = ({
  offerId,
  postThumbnail,
  setIsModalOpened,
  setPreview,
  setThumbnailInfo,
}) => {
  const DIALOG_LABEL_ID = 'label_for_aria'

  const [activeTab, setActiveTab] = useState(IMPORT_TAB_ID)
  const [credit, setCredit] = useState('')
  const [hidden, setHidden] = useState(true)
  const [step, setStep] = useState(1)
  const [tabId, setTabId] = useState(IMPORT_TAB_ID)
  const [thumbnail, setThumbnail] = useState({})
  const [url, setURL] = useState('')
  const [previewBase64, setPreviewBase64] = useState('')
  const [editedThumbnail, setEditedThumbnail] = useState('')
  const [croppingRect, setCroppingRect] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  const IMPORT_STEP = 1
  const CREDIT_STEP = 2
  const RESIZE_STEP = 3
  const PREVIEW_STEP = 4
  const VALIDATION_STEP = 5

  useEffect(() => {
    setHidden(true)
  }, [activeTab])

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  useEffect(() => {
    if (step === VALIDATION_STEP) {
      const thumbnailInfo = {
        credit: credit,
        thumbnail: thumbnail,
        croppingRect: croppingRect,
        thumbUrl: url,
      }

      setThumbnailInfo(thumbnailInfo)
      offerId && postThumbnail(offerId, thumbnailInfo)
      setPreview(editedThumbnail)
      setIsModalOpened(false)
    }
  }, [
    closeModal,
    credit,
    croppingRect,
    editedThumbnail,
    offerId,
    postThumbnail,
    setIsModalOpened,
    setPreview,
    setThumbnailInfo,
    step,
    thumbnail,
    url,
  ])

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
      hasCloseButton
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={closeModal}
    >
      <header>
        <h1
          className="tnd-header"
          id={DIALOG_LABEL_ID}
        >
          Ajouter une image
        </h1>
      </header>
      <>
        {step === IMPORT_STEP && (
          <>
            <ImportTab
              activeTab={activeTab}
              changeTab={changeTab}
              isLoading={isLoading}
            />
            {tabId === IMPORT_TAB_ID ? (
              <ImportFromComputer
                setStep={setStep}
                setThumbnail={setThumbnail}
                step={step}
              />
            ) : (
              <ImportFromURL
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                setPreviewBase64={setPreviewBase64}
                setStep={setStep}
                setURL={setURL}
                step={step}
              />
            )}
            <hr className="tnd-hr" />
            <Advices
              hidden={hidden}
              setHidden={setHidden}
            />
          </>
        )}
        {step === CREDIT_STEP && (
          <Credit
            credit={credit}
            setCredit={setCredit}
            setStep={setStep}
            step={step}
          />
        )}
        {step === RESIZE_STEP && (
          <ImageEditorWrapper
            setCroppingRect={setCroppingRect}
            setEditedThumbnail={setEditedThumbnail}
            setStep={setStep}
            step={step}
            thumbnail={thumbnail}
            url={previewBase64}
          />
        )}
        {step === PREVIEW_STEP && (
          <Preview
            preview={editedThumbnail}
            setStep={setStep}
            step={step}
          />
        )}
      </>
    </DialogBox>
  )
}

ThumbnailDialog.defaultProps = {
  offerId: undefined,
}

ThumbnailDialog.propTypes = {
  offerId: PropTypes.string,
  postThumbnail: PropTypes.func.isRequired,
  setIsModalOpened: PropTypes.func.isRequired,
  setPreview: PropTypes.func.isRequired,
  setThumbnailInfo: PropTypes.func.isRequired,
}

export default ThumbnailDialog
