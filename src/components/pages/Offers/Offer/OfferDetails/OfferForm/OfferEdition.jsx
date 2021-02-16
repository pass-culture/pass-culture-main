import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import {
  isFieldReadOnlyForSynchronizedOffer,
  isSynchronizedOffer,
} from 'components/pages/Offers/domain/localProvider'
import * as pcapi from 'repository/pcapi/pcapi'

import { computeOffersUrl } from '../../../utils/computeOffersUrl'

import { DEFAULT_FORM_VALUES, EDITED_OFFER_READ_ONLY_FIELDS } from './_constants'
import OfferForm from './OfferForm'

const computeNoDisabilityComplianceValue = offer => {
  const disabilityCompliantValues = [
    offer.audioDisabilityCompliant,
    offer.mentalDisabilityCompliant,
    offer.motorDisabilityCompliant,
    offer.visualDisabilityCompliant,
  ]

  const unknownDisabilityCompliance = disabilityCompliantValues.includes(null)
  const hasDisabilityCompliance = disabilityCompliantValues.includes(true)
  if (unknownDisabilityCompliance || hasDisabilityCompliance) {
    return false
  }

  return true
}

const OfferEdition = ({
  formValues,
  isUserAdmin,
  isLoading,
  offer,
  offersSearchFilters,
  onSubmit,
  setFormValues,
  setIsLoading,
  setPreviewOfferType,
  setShowThumbnailForm,
  showErrorNotification,
  submitErrors,
}) => {
  const [types, setTypes] = useState([])
  const [readOnlyFields, setReadOnlyFields] = useState([])
  const [initialValues, setInitialValues] = useState([])

  useEffect(function retrieveDataOnMount() {
    pcapi.loadTypes().then(receivedTypes => setTypes(receivedTypes))
  }, [])

  const computeInitialValues = offer => {
    const initialValues = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
      if (field in offer && offer[field] !== null) {
        return { ...acc, [field]: offer[field] }
      } else if (offer.extraData && field in offer.extraData) {
        return { ...acc, [field]: offer.extraData[field] }
      }
      return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
    }, {})

    initialValues.offererId = offer.venue.managingOffererId
    initialValues.noDisabilityCompliant = computeNoDisabilityComplianceValue(offer)

    return initialValues
  }

  const computeReadOnlyFields = offer => {
    if (isSynchronizedOffer(offer)) {
      return Object.keys(DEFAULT_FORM_VALUES).filter(fieldName =>
        isFieldReadOnlyForSynchronizedOffer(fieldName, offer.lastProvider)
      )
    } else {
      return EDITED_OFFER_READ_ONLY_FIELDS
    }
  }

  useEffect(() => {
    const initialValues = computeInitialValues(offer)
    const readOnlyFields = computeReadOnlyFields(offer)
    setInitialValues(initialValues)
    setReadOnlyFields(readOnlyFields)
    setIsLoading(false)
  }, [offer, setIsLoading])

  let providerName = null
  if (isSynchronizedOffer(offer)) {
    providerName = offer.lastProvider.name
  }

  if (isLoading) {
    return null
  }

  return (
    <OfferForm
      backUrl={computeOffersUrl(offersSearchFilters)}
      formValues={formValues}
      initialValues={initialValues}
      isEdition
      isUserAdmin={isUserAdmin}
      offerersNames={[
        { id: offer.venue.managingOfferer.id, name: offer.venue.managingOfferer.name },
      ]}
      onSubmit={onSubmit}
      providerName={providerName}
      readOnlyFields={readOnlyFields}
      setFormValues={setFormValues}
      setPreviewOfferType={setPreviewOfferType}
      setShowThumbnailForm={setShowThumbnailForm}
      showErrorNotification={showErrorNotification}
      submitErrors={submitErrors}
      types={types}
      venues={[offer.venue]}
    />
  )
}

OfferEdition.defaultProps = {
  isUserAdmin: false,
  offer: null,
}

OfferEdition.propTypes = {
  formValues: PropTypes.shape().isRequired,
  isLoading: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool,
  offer: PropTypes.shape(),
  offersSearchFilters: PropTypes.shape({
    name: PropTypes.string,
    offererId: PropTypes.string,
    venueId: PropTypes.string,
    typeId: PropTypes.string,
    status: PropTypes.string,
    creationMode: PropTypes.string,
    periodBeginningDate: PropTypes.string,
    periodEndingDate: PropTypes.string,
    page: PropTypes.number,
  }).isRequired,
  onSubmit: PropTypes.func.isRequired,
  setFormValues: PropTypes.func.isRequired,
  setIsLoading: PropTypes.func.isRequired,
  setPreviewOfferType: PropTypes.func.isRequired,
  setShowThumbnailForm: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
}

export default OfferEdition
