import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import {
  isFieldReadOnlyForSynchronizedOffer,
  isSynchronizedOffer,
} from 'components/pages/Offers/domain/localProvider'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'

import {
  DEFAULT_FORM_VALUES,
  EDITED_OFFER_READ_ONLY_FIELDS,
} from '../_constants'
import OfferForm from '../OfferForm'
import {
  checkHasNoDisabilityCompliance,
  getAccessibilityValues,
} from '../OfferForm/AccessibilityCheckboxList'

const OfferEdition = ({
  categories,
  isDisabled,
  isUserAdmin,
  offer,
  offersPageNumber,
  offersSearchFilters,
  onSubmit,
  setOfferPreviewData,
  showErrorNotification,
  submitErrors,
  subCategories,
  userEmail,
}) => {
  const [isLoading, setIsLoading] = useState(true)
  const [readOnlyFields, setReadOnlyFields] = useState([])
  const [initialValues, setInitialValues] = useState([])

  useEffect(() => {
    const computeInitialValues = offer => {
      let initialValues = Object.keys(DEFAULT_FORM_VALUES).reduce(
        (acc, field) => {
          if (field in offer && offer[field] !== null) {
            return { ...acc, [field]: offer[field] }
          } else if (offer.extraData && field in offer.extraData) {
            return { ...acc, [field]: offer.extraData[field] }
          }
          return { ...acc, [field]: DEFAULT_FORM_VALUES[field] }
        },
        {}
      )

      const offerAccessibility = getAccessibilityValues(offer)
      const venueAccessibility = getAccessibilityValues(offer.venue)
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
      initialValues.noDisabilityCompliant =
        checkHasNoDisabilityCompliance(offer)

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

    const initialValues = computeInitialValues(offer)
    const readOnlyFields = computeReadOnlyFields(offer)
    setInitialValues(initialValues)
    setReadOnlyFields(readOnlyFields)
    setIsLoading(false)
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
      categories={categories}
      initialValues={initialValues}
      isDisabled={isDisabled}
      isEdition
      isUserAdmin={isUserAdmin}
      offerersNames={[
        {
          id: offer.venue.managingOfferer.id,
          name: offer.venue.managingOfferer.name,
        },
      ]}
      onSubmit={onSubmit}
      providerName={providerName}
      readOnlyFields={readOnlyFields}
      setOfferPreviewData={setOfferPreviewData}
      showErrorNotification={showErrorNotification}
      subCategories={subCategories}
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
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  isDisabled: PropTypes.bool,
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
  setOfferPreviewData: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferEdition
