import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferFormContainer from './OfferForm/OfferFormContainer'
import OfferThumbnail from './OfferThumbnail/OfferThumbnail'
import OfferThumbnailPlaceholder from './OfferThumbnail/OfferThumbnailPlaceholder/OfferThumbnailPlaceholder'

const OfferDetails = props => {
  const { history, isUserAdmin, location, offer } = props

  const [formInitialValues, setFormInitialValues] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [showMediationForm, setShowMediationForm] = useState(false)

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

  useEffect(() => {
    setShowMediationForm(true)
  }, [offer])

  const handleSubmitOffer = useCallback(
    async offerValues => {
      try {
        let redirectId
        if (offer) {
          await pcapi.updateOffer(offer.id, offerValues)
          redirectId = offer.id
        } else {
          const response = await pcapi.createOffer(offerValues)
          redirectId = response.id
        }
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
        }
      }
    },
    [history, offer, setFormErrors]
  )

  let thumbnailUrl = null

  if (offer) {
    thumbnailUrl = offer.thumbUrl
  }

  return (
    <div className="offer-edit">
      <PageTitle title="Détails de l'offre" />

      <div className="sidebar-container">
        <div className="content">
          <OfferFormContainer
            initialValues={formInitialValues}
            isUserAdmin={isUserAdmin}
            offer={offer}
            onSubmit={handleSubmitOffer}
            setShowMediationForm={setShowMediationForm}
            submitErrors={formErrors}
          />
        </div>

        {showMediationForm && (
          <div className="sidebar">
            {thumbnailUrl ? <OfferThumbnail url={thumbnailUrl} /> : <OfferThumbnailPlaceholder />}
          </div>
        )}
      </div>
    </div>
  )
}

OfferDetails.propTypes = {
  isUserAdmin: PropTypes.bool.isRequired,
}

export default OfferDetails
