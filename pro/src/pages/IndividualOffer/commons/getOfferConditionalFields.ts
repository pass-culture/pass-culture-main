import type { SubcategoryResponseModel } from '@/apiClient/v1'

export const getOfferConditionalFields = ({
  offerSubcategory: offerSubCategory,
  shouldReceiveEmailNotifications = false,
}: {
  offerSubcategory: SubcategoryResponseModel
  shouldReceiveEmailNotifications?: boolean
}): string[] => {
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

  if (shouldReceiveEmailNotifications) {
    offerConditionalFields.push('bookingEmail')
  }

  if (offerSubCategory?.canBeWithdrawable) {
    offerConditionalFields.push('withdrawalType')
    offerConditionalFields.push('withdrawalDelay')
    offerConditionalFields.push('bookingContact')
  }

  return offerConditionalFields
}
