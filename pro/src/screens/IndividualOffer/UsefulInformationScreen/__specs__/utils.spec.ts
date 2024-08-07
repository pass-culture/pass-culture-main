import {
  OfferStatus,
  SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { AccessibilityEnum } from 'core/shared/types'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'

import { DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES } from '../constants'
import {
  getFilteredVenueListBySubcategory,
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from '../utils'

const virtualVenueId = 1
const secondVenueId = 2
const thirdVenueId = 3

const subCategories: SubcategoryResponseModel[] = [
  subcategoryFactory({
    id: 'ONLINE_ONLY',
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  }),
  subcategoryFactory({
    id: 'OFFLINE_ONLY',
    onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
  }),
  subcategoryFactory({
    id: 'ONLINE_OR_OFFLINE',
    onlineOfflinePlatform: CATEGORY_STATUS.ONLINE_OR_OFFLINE,
  }),
]

const virtualVenue = venueListItemFactory({
  id: virtualVenueId,
  isVirtual: true,
})

const venueList = [
  venueListItemFactory({
    id: secondVenueId,
    isVirtual: false,
  }),
  venueListItemFactory({
    id: thirdVenueId,
    isVirtual: false,
  }),
]

describe('getFilteredVenueListBySubcategory', () => {
  it('should return all venues when subCatagory is ONLINE or OFFLINE', () => {
    const result = getFilteredVenueListBySubcategory(
      [...venueList, virtualVenue],
      subCategories.find((s) => s.id === 'ONLINE_OR_OFFLINE')
    )
    expect(result.length).toEqual(3)
    expect(result[0].id).toEqual(secondVenueId)
    expect(result[1].id).toEqual(thirdVenueId)
    expect(result[2].id).toEqual(virtualVenueId)
  })

  it('should return virtual venues when subCatagory is ONLINE only', () => {
    const result = getFilteredVenueListBySubcategory(
      [...venueList, virtualVenue],
      subCategories.find((s) => s.id === 'ONLINE_ONLY')
    )
    expect(result.length).toEqual(1)
    expect(result[0].id).toEqual(virtualVenueId)
  })

  it('should return not virtual when subCatagory is OFFLINE only', () => {
    const result = getFilteredVenueListBySubcategory(
      [...venueList, virtualVenue],
      subCategories.find((s) => s.id === 'OFFLINE_ONLY')
    )
    expect(result.length).toEqual(2)
    expect(result[0].id).toEqual(secondVenueId)
    expect(result[1].id).toEqual(thirdVenueId)
  })
})

const mockOffer = getIndividualOfferFactory({
  isEvent: true,
  isNational: false,
  withdrawalDetails: 'Detailed info',
  withdrawalDelay: 3,
  withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
  visualDisabilityCompliant: true,
  mentalDisabilityCompliant: false,
  audioDisabilityCompliant: true,
  motorDisabilityCompliant: false,
  bookingEmail: 'test@example.com',
  bookingContact: 'Contact Info',
  url: 'http://example.com',
  externalTicketOfficeUrl: 'http://external.com',
})

describe('setDefaultInitialValuesFromOffer', () => {
  it('should set default initial values from offer correctly', () => {
    const expectedValues = {
      isEvent: true,
      isNational: false,
      isVenueVirtual: false,
      withdrawalDetails: 'Detailed info',
      withdrawalDelay: 3,
      withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
      accessibility: {
        [AccessibilityEnum.VISUAL]: true,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: true,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: false,
      },
      bookingEmail: 'test@example.com',
      bookingContact: 'Contact Info',
      receiveNotificationEmails: true,
      url: 'http://example.com',
      externalTicketOfficeUrl: 'http://external.com',
    }

    const result = setDefaultInitialValuesFromOffer(mockOffer)

    expect(result).toEqual(expectedValues)
  })

  it('should handle default values for missing properties in the offer', () => {
    const mockOfferWithMissingProperties = getIndividualOfferFactory({
      isEvent: false,
      isNational: true,
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      audioDisabilityCompliant: false,
      motorDisabilityCompliant: false,
    })

    const expectedValues = {
      isEvent: false,
      isNational: true,
      isVenueVirtual: false,
      withdrawalDetails:
        DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['withdrawalDetails'],
      withdrawalDelay: undefined,
      withdrawalType: undefined,
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: true,
      },
      bookingEmail: '',
      bookingContact: undefined,
      receiveNotificationEmails: false,
      url: DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['url'],
      externalTicketOfficeUrl:
        DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['externalTicketOfficeUrl'],
    }

    const result = setDefaultInitialValuesFromOffer(
      mockOfferWithMissingProperties
    )

    expect(result).toEqual(expectedValues)
  })

  it('should handle accessibility not set', () => {
    const mockOfferWithMissingProperties = getIndividualOfferFactory({
      isEvent: false,
      isNational: true,
      visualDisabilityCompliant: undefined,
      mentalDisabilityCompliant: undefined,
      audioDisabilityCompliant: undefined,
      motorDisabilityCompliant: undefined,
    })

    const expectedValues = {
      isEvent: false,
      isNational: true,
      isVenueVirtual: false,
      withdrawalDetails:
        DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['withdrawalDetails'],
      withdrawalDelay: undefined,
      withdrawalType: undefined,
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: false,
      },
      bookingEmail: '',
      bookingContact: undefined,
      receiveNotificationEmails: false,
      url: DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['url'],
      externalTicketOfficeUrl:
        DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES['externalTicketOfficeUrl'],
    }

    const result = setDefaultInitialValuesFromOffer(
      mockOfferWithMissingProperties
    )

    expect(result).toEqual(expectedValues)
  })

  it('should handle null withdrawalDelay correctly', () => {
    const mockOfferWithNullWithdrawalDelay = getIndividualOfferFactory({
      ...mockOffer,
      withdrawalDelay: null,
    })

    const expectedValues = {
      ...setDefaultInitialValuesFromOffer(mockOffer),
      withdrawalDelay: undefined,
    }

    const result = setDefaultInitialValuesFromOffer(
      mockOfferWithNullWithdrawalDelay
    )

    expect(result).toEqual(expectedValues)
  })
})

describe('setFormReadOnlyFields', () => {
  it('should return all fields as read only when offer is rejected', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.REJECTED,
    })

    const result = setFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES)
    )
  })

  it('should return all fields as read only when offer is pending', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PENDING,
    })

    const result = setFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFULL_INFORMATION_INTITIAL_VALUES)
    )
  })

  it('should return some fields as not read only when offer is synchronized', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Allocine' },
    })

    const result = setFormReadOnlyFields(offer)

    expect(result).not.toContain(['accessibility', 'externalTicketOfficeUrl'])
  })
})
