import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'

import Spinner from 'components/layout/Spinner'
import {
  isFieldReadOnlyForSynchronizedOffer,
  isSynchronizedOffer,
} from 'components/pages/Offers/domain/localProvider'
import { EDITED_OFFER_READ_ONLY_FIELDS } from 'core/Offers'
import { computeOffersUrl } from 'core/Offers/utils'

import { DEFAULT_FORM_VALUES } from '../_constants'
import OfferForm from '../OfferForm'

const OfferEdition = ({
  categories,
  initialValues,
  isCreatingOffer,
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

  useEffect(() => {
    const computeReadOnlyFields = offer => {
      if (isDisabled) {
        return Object.keys(DEFAULT_FORM_VALUES).filter(() => true)
      } else if (isSynchronizedOffer(offer)) {
        return Object.keys(DEFAULT_FORM_VALUES).filter(fieldName =>
          isFieldReadOnlyForSynchronizedOffer(fieldName, offer.lastProvider)
        )
      } else {
        let readOnlyFields = [...EDITED_OFFER_READ_ONLY_FIELDS]
        if (
          !readOnlyFields.includes('showType') &&
          offer?.extraData?.showType
        ) {
          readOnlyFields.push('showType')
          readOnlyFields.push('showSubType')
        }
        if (
          !readOnlyFields.includes('musicType') &&
          offer?.extraData?.musicType
        ) {
          readOnlyFields.push('musicType')
          readOnlyFields.push('musicSubType')
        }
        return readOnlyFields
      }
    }

    const readOnlyFields = computeReadOnlyFields(offer)
    setReadOnlyFields(readOnlyFields)
    setIsLoading(false)
  }, [isDisabled, offer, setIsLoading])

  let providerName = null
  if (isSynchronizedOffer(offer)) {
    providerName = offer.lastProvider.name
  }
  const backUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)
  if (isLoading) {
    return <Spinner />
  }

  return (
    <OfferForm
      backUrl={backUrl}
      categories={categories}
      initialValues={initialValues}
      isDisabled={isDisabled}
      isEdition={!isCreatingOffer}
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
      setReadOnlyFields={setReadOnlyFields}
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
  isCreatingOffer: false,
}

OfferEdition.propTypes = {
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  initialValues: PropTypes.shape().isRequired,
  isCreatingOffer: PropTypes.bool,
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
