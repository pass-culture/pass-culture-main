import { SubcategoryResponseModel } from '@/apiClient/v1'

export const getOfferConditionalFields = ({
  offerSubcategory,
  receiveNotificationEmails = null,
}: {
  offerSubcategory: SubcategoryResponseModel
  receiveNotificationEmails?: boolean | null
}): string[] => {
  const offerConditionalFields = []

  if (offerSubcategory.isEvent) {
    offerConditionalFields.push('durationMinutes')
  }

  if (offerSubcategory.canBeDuo) {
    offerConditionalFields.push('isDuo')
  }

  if (offerSubcategory.conditionalFields.includes('musicType')) {
    offerConditionalFields.push('musicSubType')
  }

  if (offerSubcategory.conditionalFields.includes('showType')) {
    offerConditionalFields.push('showSubType')
  }

  if (receiveNotificationEmails) {
    offerConditionalFields.push('bookingEmail')
  }

  if (offerSubcategory.canBeWithdrawable) {
    offerConditionalFields.push('withdrawalType')
    offerConditionalFields.push('withdrawalDelay')
    offerConditionalFields.push('bookingContact')
  }

  return offerConditionalFields
}
