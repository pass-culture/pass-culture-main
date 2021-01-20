import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferCreation from './OfferForm/OfferCreation'
import OfferEditionContainer from './OfferForm/OfferEditionContainer'
import OfferThumbnail from './OfferThumbnail/OfferThumbnail'
import OfferThumbnailPlaceholder from './OfferThumbnail/OfferThumbnailPlaceholder/OfferThumbnailPlaceholder'

const OfferDetails = ({
  history,
  isUserAdmin,
  location,
  offer,
  showCreationSuccessNotification,
  showEditionSuccessNotification,
  showErrorNotification,
}) => {
  const [formInitialValues, setFormInitialValues] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [showThumbnailForm, setShowThumbnailForm] = useState(offer !== null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search)
    if (queryParams.get('structure')) {
      setFormInitialValues(oldFormInitialValues => ({
        ...oldFormInitialValues,
        offererId: queryParams.get('structure'),
      }))
    }
    if (queryParams.get('lieu')) {
      setFormInitialValues(oldFormInitialValues => ({
        ...oldFormInitialValues,
        venueId: queryParams.get('lieu'),
      }))
    }
  }, [setFormInitialValues, location.search])

  const handleSubmitOffer = useCallback(
    async offerValues => {
      try {
        let redirectId
        if (offer) {
          await pcapi.updateOffer(offer.id, offerValues)
          showEditionSuccessNotification()
          redirectId = offer.id
        } else {
          const response = await pcapi.createOffer(offerValues)
          showCreationSuccessNotification()
          redirectId = response.id
        }
        setFormErrors({})
        history.push(`/offres/v2/${redirectId}/edition`)
      } catch (error) {
        if (error && 'errors' in error) {
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
      history,
      offer,
      setFormErrors,
      showCreationSuccessNotification,
      showEditionSuccessNotification,
      showErrorNotification,
    ]
  )

  return (
    <div className="offer-edit">
      <PageTitle title="Détails de l'offre" />

      {isLoading && <Spinner />}

      <div className="sidebar-container">
        <div className="content">
          {offer ? (
            <OfferEditionContainer
              isLoading={isLoading}
              isUserAdmin={isUserAdmin}
              offer={offer}
              onSubmit={handleSubmitOffer}
              setIsLoading={setIsLoading}
              setShowThumbnailForm={setShowThumbnailForm}
              showErrorNotification={showErrorNotification}
              submitErrors={formErrors}
            />
          ) : (
            <OfferCreation
              initialValues={formInitialValues}
              isLoading={isLoading}
              isUserAdmin={isUserAdmin}
              onSubmit={handleSubmitOffer}
              setIsLoading={setIsLoading}
              setShowThumbnailForm={setShowThumbnailForm}
              showErrorNotification={showErrorNotification}
              submitErrors={formErrors}
            />
          )}
        </div>

        {showThumbnailForm && (
          <div className="sidebar">
            {offer?.thumbUrl ? (
              <OfferThumbnail url={offer.thumbUrl} />
            ) : (
              <OfferThumbnailPlaceholder />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

OfferDetails.defaultProps = {
  offer: null,
}

OfferDetails.propTypes = {
  history: PropTypes.shape().isRequired,
  isUserAdmin: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  offer: PropTypes.shape(),
  showCreationSuccessNotification: PropTypes.func.isRequired,
  showEditionSuccessNotification: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
}

export default OfferDetails
