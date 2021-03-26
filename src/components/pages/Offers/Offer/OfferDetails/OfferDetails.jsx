import PropTypes from 'prop-types'
import React, { useCallback, useRef, useState } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import OfferPreviewLink from 'components/pages/Offers/Offer/OfferPreviewLink/OfferPreviewLink'
import * as pcapi from 'repository/pcapi/pcapi'

import { OFFER_STATUS } from '../../Offers/domain/offerStatus'

import OfferCreation from './OfferForm/OfferCreation'
import OfferEditionContainer from './OfferForm/OfferEditionContainer'
import OfferPreview from './OfferPreview/OfferPreview'
import OfferStatusBanner from './OfferStatusBanner/OfferStatusBanner'
import OfferThumbnail from './OfferThumbnail/OfferThumbnail'

const OfferDetails = ({
  history,
  isUserAdmin,
  location,
  offer,
  reloadOffer,
  showCreationSuccessNotification,
  showEditionSuccessNotification,
  showErrorNotification,
  userEmail,
}) => {
  const initialValues = {}
  const queryParams = new URLSearchParams(location.search)
  if (queryParams.has('structure')) {
    initialValues.offererId = queryParams.get('structure')
  }
  if (queryParams.has('lieu')) {
    initialValues.venueId = queryParams.get('lieu')
  }

  const formInitialValues = useRef(initialValues)
  const [formValues, setFormValues] = useState({})
  const [offerType, setOfferType] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [showThumbnailForm, setShowThumbnailForm] = useState(false)
  const [thumbnailInfo, setThumbnailInfo] = useState({})
  const [thumbnailError, setThumbnailError] = useState(false)

  const handleSubmitOffer = useCallback(
    async offerValues => {
      try {
        if (offer) {
          await pcapi.updateOffer(offer.id, offerValues)
          showEditionSuccessNotification()
          const offerThumbnailHasBeenUpdated = Object.values(thumbnailInfo).length > 0
          if (offerThumbnailHasBeenUpdated) {
            const { credit, thumbnail, croppingRect, thumbUrl } = thumbnailInfo
            await pcapi.postThumbnail(
              formValues.offererId,
              offer.id,
              credit,
              thumbnail,
              thumbUrl,
              croppingRect?.x,
              croppingRect?.y,
              croppingRect?.height
            )
          }
          reloadOffer()
          setFormErrors({})
        } else {
          const response = await pcapi.createOffer(offerValues)
          const createdOfferId = response.id
          const offerThumbnailHasBeenUploaded = Object.values(thumbnailInfo).length > 0
          if (offerThumbnailHasBeenUploaded) {
            const { credit, thumbnail, croppingRect, thumbUrl } = thumbnailInfo
            await pcapi.postThumbnail(
              formValues.offererId,
              createdOfferId,
              credit,
              thumbnail,
              thumbUrl,
              croppingRect?.x,
              croppingRect?.y,
              croppingRect?.height
            )
          }
          showCreationSuccessNotification()
          history.push(`/offres/${createdOfferId}/stocks`)
        }
      } catch (error) {
        if (error && 'errors' in error) {
          if (error.errors.errors) {
            setThumbnailError(true)
          }
          const mapApiErrorsToFormErrors = {
            venue: 'venueId',
          }
          let newFormErrors = {}
          let formFieldName
          for (let apiFieldName in error.errors) {
            formFieldName = apiFieldName
            if (apiFieldName in mapApiErrorsToFormErrors) {
              formFieldName = mapApiErrorsToFormErrors[apiFieldName]
            }
            newFormErrors[formFieldName] = error.errors[apiFieldName]
          }
          setFormErrors(newFormErrors)
          showErrorNotification()
        }
      }
    },
    [
      formValues.offererId,
      history,
      offer,
      reloadOffer,
      showCreationSuccessNotification,
      showEditionSuccessNotification,
      showErrorNotification,
      thumbnailInfo,
    ]
  )

  const offerStatus = offer?.status
  const needsStatusInfosMessage = offerStatus
    ? [OFFER_STATUS.REJECTED, OFFER_STATUS.AWAITING].includes(offerStatus)
    : false

  return (
    <>
      <PageTitle title="Détails de l'offre" />

      <div className={Object.entries(formValues).length !== 0 ? 'sidebar-container' : ''}>
        <div className="content">
          {offer ? (
            <>
              {needsStatusInfosMessage && <OfferStatusBanner status={offerStatus} />}
              <OfferEditionContainer
                formValues={formValues}
                isUserAdmin={isUserAdmin}
                offer={offer}
                onSubmit={handleSubmitOffer}
                setFormValues={setFormValues}
                setPreviewOfferType={setOfferType}
                setShowThumbnailForm={setShowThumbnailForm}
                showErrorNotification={showErrorNotification}
                submitErrors={formErrors}
                userEmail={userEmail}
              />
            </>
          ) : (
            <OfferCreation
              formValues={formValues}
              initialValues={formInitialValues.current}
              isUserAdmin={isUserAdmin}
              onSubmit={handleSubmitOffer}
              setFormValues={setFormValues}
              setPreviewOfferType={setOfferType}
              setShowThumbnailForm={setShowThumbnailForm}
              showErrorNotification={showErrorNotification}
              submitErrors={formErrors}
              userEmail={userEmail}
            />
          )}
        </div>

        {showThumbnailForm && (
          <div className="sidebar">
            <div className="sidebar-wrapper">
              <OfferThumbnail
                setThumbnailInfo={setThumbnailInfo}
                thumbnailError={thumbnailError}
                url={offer?.thumbUrl}
              />
              <OfferPreview
                formValues={formValues}
                offerType={offerType}
              />
            </div>
            {offer ? (
              <OfferPreviewLink
                mediationId={offer.activeMediation ? offer.activeMediation.id : null}
                offerId={offer.id}
              />
            ) : null}
          </div>
        )}
      </div>
    </>
  )
}

OfferDetails.defaultProps = {
  offer: null,
  reloadOffer: null,
}

OfferDetails.propTypes = {
  history: PropTypes.shape().isRequired,
  isUserAdmin: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  offer: PropTypes.shape(),
  reloadOffer: PropTypes.func,
  showCreationSuccessNotification: PropTypes.func.isRequired,
  showEditionSuccessNotification: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferDetails
