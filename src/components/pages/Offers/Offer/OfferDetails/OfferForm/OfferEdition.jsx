/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import Spinner from 'components/layout/Spinner'
import {
  isFieldReadOnlyForSynchronizedOffer,
  isSynchronizedOffer,
} from 'components/pages/Offers/domain/localProvider'
import {
  DEFAULT_FORM_VALUES,
  EDITED_OFFER_READ_ONLY_FIELDS,
} from 'components/pages/Offers/Offer/OfferDetails/OfferForm/_constants'
import { getDisabilityComplianceValues } from 'components/pages/Offers/Offer/OfferDetails/OfferForm/AccessibilityCheckboxList'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'

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
  if (hasDisabilityCompliance || unknownDisabilityCompliance) {
    return false
  }

  return true
}

const OfferEdition = ({
  formValues,
  isDisabled,
  isSubmitLoading,
  isUserAdmin,
  offer,
  offersPageNumber,
  offersSearchFilters,
  onSubmit,
  setFormValues,
  setPreviewOfferCategory,
  showErrorNotification,
  submitErrors,
  userEmail,
}) => {
  const [isLoading, setIsLoading] = useState(true)
  const { subCategories } = useSelector(state => state.offers.categories)
  const [readOnlyFields, setReadOnlyFields] = useState([])
  const [initialValues, setInitialValues] = useState([])

  useEffect(() => {
    const computeInitialValues = offer => {
      let initialValues = Object.keys(DEFAULT_FORM_VALUES).reduce((acc, field) => {
        if (field in offer && offer[field] !== null) {
          return { ...acc, [field]: offer[field] }
        } else if (offer.extraData && field in offer.extraData) {
          return { ...acc, [field]: offer.extraData[field] }
        }
        return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
      }, {})

      const offerAccessibility = getDisabilityComplianceValues(offer)
      const venueAccessibility = getDisabilityComplianceValues(offer.venue)
      if (
        Object.values(offerAccessibility).includes(null) &&
        !Object.values(venueAccessibility).includes(null)
      ) {
        initialValues = { ...initialValues, ...venueAccessibility }
      }

      initialValues.categoryId = subCategories.find(
        subCategory => subCategory.id === offer.subcategoryId
      ).categoryId

      initialValues.subcategoryId = offer.subcategoryId
      initialValues.offererId = offer.venue.managingOffererId
      initialValues.noDisabilityCompliant = computeNoDisabilityComplianceValue(offer)

      return initialValues
    }

    const computeReadOnlyFields = offer => {
      if (isDisabled) {
        return Object.keys(DEFAULT_FORM_VALUES).filter(() => true)
      } else if (isSynchronizedOffer(offer)) {
        return Object.keys(DEFAULT_FORM_VALUES).filter(fieldName =>
          isFieldReadOnlyForSynchronizedOffer(fieldName, offer.lastProvider)
        )
      } else {
        return EDITED_OFFER_READ_ONLY_FIELDS
      }
    }

    if (subCategories) {
      const initialValues = computeInitialValues(offer)
      const readOnlyFields = computeReadOnlyFields(offer)
      setInitialValues(initialValues)
      setReadOnlyFields(readOnlyFields)
      setIsLoading(false)
    }
  }, [isDisabled, offer, setIsLoading, subCategories])

  let providerName = null
  if (isSynchronizedOffer(offer)) {
    providerName = offer.lastProvider.name
  }

  if (isLoading) {
    return <Spinner />
  }

  return (
    <OfferForm
      backUrl={computeOffersUrl(offersSearchFilters, offersPageNumber)}
      formValues={formValues}
      initialValues={initialValues}
      isDisabled={isDisabled}
      isEdition
      isSubmitLoading={isSubmitLoading}
      isUserAdmin={isUserAdmin}
      offerersNames={[
        { id: offer.venue.managingOfferer.id, name: offer.venue.managingOfferer.name },
      ]}
      onSubmit={onSubmit}
      providerName={providerName}
      readOnlyFields={readOnlyFields}
      setFormValues={setFormValues}
      setPreviewOfferCategory={setPreviewOfferCategory}
      showErrorNotification={showErrorNotification}
      submitErrors={submitErrors}
      userEmail={userEmail}
      venues={[offer.venue]}
    />
  )
}

OfferEdition.defaultProps = {
  isDisabled: false,
  isUserAdmin: false,
  offer: null,
}

OfferEdition.propTypes = {
  formValues: PropTypes.shape().isRequired,
  isDisabled: PropTypes.bool,
  isSubmitLoading: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool,
  offer: PropTypes.shape(),
  offersPageNumber: PropTypes.number.isRequired,
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
  setPreviewOfferCategory: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferEdition
