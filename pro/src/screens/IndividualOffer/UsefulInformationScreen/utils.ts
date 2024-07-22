import {
  GetIndividualOfferResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { AccessibilityEnum } from 'core/shared/types'

import { DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES } from './constants'
import { UsefulInformationFormValues } from './types'

export const getFilteredVenueListBySubcategory = (
  venueList: VenueListItemResponseModel[],
  subcategory?: SubcategoryResponseModel
): VenueListItemResponseModel[] => {
  if (!subcategory) {
    return venueList
  }

  if (subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return venueList
  }

  return venueList.filter((venue) =>
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}

export function setDefaultInitialValuesFromOffer(
  offer: GetIndividualOfferResponseModel
): UsefulInformationFormValues {
  const baseAccessibility = {
    [AccessibilityEnum.VISUAL]: offer.visualDisabilityCompliant || false,
    [AccessibilityEnum.MENTAL]: offer.mentalDisabilityCompliant || false,
    [AccessibilityEnum.AUDIO]: offer.audioDisabilityCompliant || false,
    [AccessibilityEnum.MOTOR]: offer.motorDisabilityCompliant || false,
  }
  return {
    isEvent: offer.isEvent,
    isNational: offer.isNational,
    withdrawalDetails:
      offer.withdrawalDetails ||
      DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['withdrawalDetails'],
    withdrawalDelay:
      offer.withdrawalDelay === null ? undefined : offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType || undefined,
    accessibility: {
      ...baseAccessibility,
      [AccessibilityEnum.NONE]:
        !Object.values(baseAccessibility).includes(true),
    },
    bookingEmail: offer.bookingEmail || '',
    bookingContact: offer.bookingContact || undefined,
    receiveNotificationEmails: !!offer.bookingEmail,
    url: offer.url || DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['url'],
    externalTicketOfficeUrl:
      offer.externalTicketOfficeUrl ||
      DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['externalTicketOfficeUrl'],
  }
}
