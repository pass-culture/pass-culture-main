import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { AccessibilityEnum } from 'core/shared/types'

import { FORM_DEFAULT_VALUES } from '../constants'
import { IndividualOfferFormValues } from '../types'

import { buildSubcategoryFields } from './buildSubCategoryFields'

export const buildAccessibilityFormValues = (
  venue: VenueListItemResponseModel
) => {
  if (venue.externalAccessibilityData) {
    return {
      [AccessibilityEnum.VISUAL]: Boolean(
        venue.externalAccessibilityData.isAccessibleVisualDisability
      ),
      [AccessibilityEnum.MENTAL]: Boolean(
        venue.externalAccessibilityData.isAccessibleMentalDisability
      ),
      [AccessibilityEnum.AUDIO]: Boolean(
        venue.externalAccessibilityData.isAccessibleAudioDisability
      ),
      [AccessibilityEnum.MOTOR]: Boolean(
        venue.externalAccessibilityData.isAccessibleMotorDisability
      ),
      [AccessibilityEnum.NONE]: [
        venue.externalAccessibilityData.isAccessibleVisualDisability,
        venue.externalAccessibilityData.isAccessibleMentalDisability,
        venue.externalAccessibilityData.isAccessibleAudioDisability,
        venue.externalAccessibilityData.isAccessibleMotorDisability,
      ].every((accessibility) => accessibility === false),
    }
  }

  return {
    [AccessibilityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessibilityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessibilityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessibilityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
    [AccessibilityEnum.NONE]: [
      venue.visualDisabilityCompliant,
      venue.mentalDisabilityCompliant,
      venue.audioDisabilityCompliant,
      venue.motorDisabilityCompliant,
    ].every((accessibility) => accessibility === false),
  }
}

export const setDefaultInitialFormValues = (
  offererNames: GetOffererNameResponseModel[],
  offererId: string | null,
  venueId: string | null,
  venueList: VenueListItemResponseModel[],
  isBookingContactEnabled: boolean
): IndividualOfferFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId

  if (offererNames.length === 1) {
    initialOffererId = offererNames[0].id.toString()
  } else if (
    offererId &&
    offererNames.find((offerer) => offerer.id.toString() === offererId)
  ) {
    initialOffererId = offererId
  }

  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  const initialIsVenueVirtual = venueList.every((v) => v.isVirtual)

  const venue =
    venueList.length === 1
      ? venueList[0]
      : venueList.find((venue) => venue.id.toString() === venueId)

  if (venue) {
    initialAccessibility = buildAccessibilityFormValues(venue)

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  const { subcategoryFields } = buildSubcategoryFields(isBookingContactEnabled)

  return {
    ...FORM_DEFAULT_VALUES,
    isDuo: FORM_DEFAULT_VALUES.isDuo,
    categoryId: FORM_DEFAULT_VALUES.categoryId,
    subcategoryId: FORM_DEFAULT_VALUES.subcategoryId,
    subCategoryFields: subcategoryFields,
    offererId: initialOffererId,
    venueId: venue?.id ? String(venue.id) : FORM_DEFAULT_VALUES.venueId,
    withdrawalDetails: initialWithdrawalDetails,
    accessibility: initialAccessibility,
    isVenueVirtual: initialIsVenueVirtual,
  }
}
