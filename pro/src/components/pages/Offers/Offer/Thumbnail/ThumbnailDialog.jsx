import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import {
  IMPORT_TAB_ID,
  NBSP,
} from 'components/pages/Offers/Offer/Thumbnail/_constants'
import Credit from 'components/pages/Offers/Offer/Thumbnail/Credit/Credit'
import ImageEditorWrapper from 'components/pages/Offers/Offer/Thumbnail/ImageEditor/ImageEditorWrapper'
import ImportFromComputer from 'components/pages/Offers/Offer/Thumbnail/ImportFromComputer/ImportFromComputer'
import OfferPreview from 'components/pages/Offers/Offer/Thumbnail/Preview/OfferPreview'
import Advices from 'new_components/Advices/Advices'
import DialogBox from 'new_components/DialogBox/DialogBox'

const ThumbnailDialog = ({
  offerId,
  postThumbnail,
  setIsModalOpened,
  setPreview,
  setThumbnailInfo,
}) => {
  const DIALOG_LABEL_ID = 'label_for_aria'
  const activeTab = IMPORT_TAB_ID

  const [credit, setCredit] = useState('')
  const [hidden, setHidden] = useState(true)
  const [step, setStep] = useState(1)
  const [thumbnail, setThumbnail] = useState({})
  const [editedThumbnail, setEditedThumbnail] = useState('')
  const [croppingRect, setCroppingRect] = useState({})

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
  ])

  const advicesDescription = `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition${NBSP}:`

  return (
    <DialogBox
      extraClassNames={
        step === 1 ? 'thumbnail-dialog tnd-step1' : 'thumbnail-dialog'
      }
      hasCloseButton
      labelledBy={DIALOG_LABEL_ID}
      onDismiss={closeModal}
    >
      <header>
        <h1 className="tnd-header" id={DIALOG_LABEL_ID}>
          Ajouter une image
        </h1>
      </header>
      <>
        {step === IMPORT_STEP && (
          <>
            <ImportFromComputer
              setStep={setStep}
              setThumbnail={setThumbnail}
              step={step}
            />
            <hr className="tnd-hr" />
            <Advices
              hidden={hidden}
              setHidden={setHidden}
              teaserText={advicesDescription}
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
          />
        )}
        {step === PREVIEW_STEP && (
          <OfferPreview
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
