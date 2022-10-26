import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import Spinner from 'components/layout/Spinner'
import {
  isFieldReadOnlyForSynchronizedOffer,
  isSynchronizedOffer,
} from 'components/pages/Offers/domain/localProvider'
import { EDITED_OFFER_READ_ONLY_FIELDS } from 'core/Offers'
import { computeOffersUrl } from 'core/Offers/utils'
import {
  searchFiltersSelector,
  searchPageNumberSelector,
} from 'store/offers/selectors'

import { DEFAULT_FORM_VALUES } from '../_constants'
import OfferForm from '../OfferForm'

const OfferEdition = ({
  categories,
  initialValues,
  isCreatingOffer,
  isDisabled,
  isUserAdmin,
  offer,
  onSubmit,
  setOfferPreviewData,
  showErrorNotification,
  submitErrors,
  subCategories,
  userEmail,
}) => {
  const [isLoading, setIsLoading] = useState(true)
  const [readOnlyFields, setReadOnlyFields] = useState([])
  const offersSearchFilters = useSelector(searchFiltersSelector)
  const offersPageNumber = useSelector(searchPageNumberSelector)

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
      offer={offer}
    />
  )
}

OfferEdition.defaultProps = {
  isDisabled: false,
  isUserAdmin: false,
  offer: undefined,
  isCreatingOffer: false,
}

OfferEdition.propTypes = {
  categories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  initialValues: PropTypes.shape().isRequired,
  isCreatingOffer: PropTypes.bool,
  isDisabled: PropTypes.bool,
  isUserAdmin: PropTypes.bool,
  offer: PropTypes.shape(),
  onSubmit: PropTypes.func.isRequired,
  setOfferPreviewData: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  subCategories: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  submitErrors: PropTypes.shape().isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferEdition
