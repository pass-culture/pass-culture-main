import { SubcategoryResponseModel } from 'apiClient/v1'

interface GetOfferConditionalFieldsProps {
  offerSubCategory?: SubcategoryResponseModel | null
  isUserAdmin?: boolean | null
  receiveNotificationEmails?: boolean | null
  isVenueVirtual?: boolean | null
}

export const getOfferConditionalFields = ({
  offerSubCategory = null,
  isUserAdmin = null,
  receiveNotificationEmails = null,
  isVenueVirtual = null,
}: GetOfferConditionalFieldsProps): string[] => {
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

  if (offerSubCategory?.canBeWithdrawable) {
    offerConditionalFields.push('withdrawalType')
    offerConditionalFields.push('withdrawalDelay')
    offerConditionalFields.push('bookingContact')
  }

  return offerConditionalFields
}
