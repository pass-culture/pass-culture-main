import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferFormContainer from './OfferForm/OfferFormContainer'
import OfferPreviewLink from './OfferPreviewLink/OfferPreviewLink'
import OfferPreviewPlaceholder from './OfferPreviewPlaceholder/OfferPreviewPlaceholder'

const OfferDetails = props => {
  const { history, isUserAdmin, location, match } = props

  const [offer, setOffer] = useState(null)
  const [formInitialValues, setFormInitialValues] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [isTypeSelected, setIsTypeSelected] = useState(true)

  useEffect(() => {
    async function loadOffer(offerId) {
      const existingOffer = await pcapi.loadOffer(offerId)
      setOffer(existingOffer)
    }

    if (match.params.offerId) {
      loadOffer(match.params.offerId)
    }
  }, [match.params.offerId])

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

  let pageTitle = 'Nouvelle offre'
  let mediationId = null
  if (offer) {
    pageTitle = 'Éditer une offre'
    mediationId = offer.activeMediation ? offer.activeMediation.id : null
  }

  const actionLink = offer && (
    <OfferPreviewLink
      mediationId={mediationId}
      offerId={offer.id}
    />
  )

  return (
    <div className="offer-page-v2">
      <PageTitle title={pageTitle} />
      <Titles
        action={actionLink}
        title={pageTitle}
      />

      <div className="offer-content">
        <OfferFormContainer
          initialValues={formInitialValues}
          isUserAdmin={isUserAdmin}
          offer={offer}
          onSubmit={handleSubmitOffer}
          setIsTypeSelected={setIsTypeSelected}
          submitErrors={formErrors}
        />
        {isTypeSelected && (
          <div>
            <OfferPreviewPlaceholder />
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
