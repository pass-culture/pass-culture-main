import { IOfferSubCategory } from 'core/Offers/types'

import { WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE } from '../components/pages/Offers/Offer/OfferDetails/_constants'

interface IGetOfferConditionalFieldsProps {
  offerSubCategory?: IOfferSubCategory | null
  isUserAdmin?: boolean | null
  receiveNotificationEmails?: boolean | null
  isVenueVirtual?: boolean | null
}

export const getOfferConditionalFields = ({
  offerSubCategory = null,
  isUserAdmin = null,
  receiveNotificationEmails = null,
  isVenueVirtual = null,
}: IGetOfferConditionalFieldsProps): string[] => {
  const offerConditionalFields = []

  if (offerSubCategory?.isEvent) {
    offerConditionalFields.push('durationMinutes')
  }

  if (offerSubCategory?.canBeDuo) {
    offerConditionalFields.push('isDuo')
  }

  if (offerSubCategory?.conditionalFields.includes('musicType')) {
    offerConditionalFields.push('musicSubType')
  }

  if (offerSubCategory?.conditionalFields.includes('showType')) {
    offerConditionalFields.push('showSubType')
  }

  if (isUserAdmin) {
    offerConditionalFields.push('isNational')
  }

  if (receiveNotificationEmails) {
    offerConditionalFields.push('bookingEmail')
  }

  if (isVenueVirtual) {
    offerConditionalFields.push('url')
  }

  if (
    offerSubCategory &&
    WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(offerSubCategory.id)
  ) {
    offerConditionalFields.push('withdrawalType')
    offerConditionalFields.push('withdrawalDelay')
  }

  return offerConditionalFields
}
