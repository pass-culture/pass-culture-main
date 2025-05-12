import { OfferStatus, WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from '../constants'
import {
  setDefaultInitialValuesFromOffer,
  setFormReadOnlyFields,
} from '../utils'

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
  externalTicketOfficeUrl: 'https://hello.co',
  url: 'http://example.com',
})

describe('setDefaultInitialValuesFromOffer', () => {
  it('should set default initial values from offer correctly', () => {
    const expectedValues = {
      isEvent: true,
      isNational: false,
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
      externalTicketOfficeUrl: 'https://hello.co',
      bookingContact: 'Contact Info',
      receiveNotificationEmails: true,
    }

    const result = setDefaultInitialValuesFromOffer({ offer: mockOffer })

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
      externalTicketOfficeUrl: undefined,
    })

    const expectedValues = {
      isEvent: false,
      isNational: true,
      withdrawalDetails:
        DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES['withdrawalDetails'],
      withdrawalDelay: undefined,
      withdrawalType: WithdrawalTypeEnum.NO_TICKET,
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: true,
      },
      bookingEmail: '',
      bookingContact: undefined,
      externalTicketOfficeUrl: undefined,
      receiveNotificationEmails: false,
    }

    const result = setDefaultInitialValuesFromOffer({
      offer: mockOfferWithMissingProperties,
    })

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
      externalTicketOfficeUrl: undefined,
    })

    const expectedValues = {
      isEvent: false,
      isNational: true,
      withdrawalDetails:
        DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES['withdrawalDetails'],
      withdrawalDelay: undefined,
      withdrawalType: WithdrawalTypeEnum.NO_TICKET,
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: false,
      },
      bookingEmail: '',
      bookingContact: undefined,
      externalTicketOfficeUrl: undefined,
      receiveNotificationEmails: false,
    }

    const result = setDefaultInitialValuesFromOffer({
      offer: mockOfferWithMissingProperties,
    })

    expect(result).toEqual(expectedValues)
  })

  it('should handle null withdrawalDelay correctly', () => {
    const mockOfferWithNullWithdrawalDelay = getIndividualOfferFactory({
      ...mockOffer,
      withdrawalDelay: null,
    })

    const expectedValues = {
      ...setDefaultInitialValuesFromOffer({ offer: mockOffer }),
      withdrawalDelay: undefined,
    }

    const result = setDefaultInitialValuesFromOffer({
      offer: mockOfferWithNullWithdrawalDelay,
    })

    expect(result).toEqual(expectedValues)
  })

  it('should handle address fields', () => {
    mockOffer.address = {
      id: 1,
      id_oa: 997,
      isLinkedToVenue: true,
      isManualEdition: true,
      latitude: 48.85332,
      longitude: 2.348979,
      postalCode: '75001',
      street: '3 rue de Valois',
      city: 'Paris',
      label: 'Bureau',
      banId: '35288_7283_00001',
    }

    const { street, postalCode, city, latitude, longitude } = mockOffer.address!
    const addressAutocomplete = `${street} ${postalCode} ${city}`
    const coords = `${latitude}, ${longitude}`

    const expectedValues = {
      isEvent: true,
      isNational: false,
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
      externalTicketOfficeUrl: 'https://hello.co',
      receiveNotificationEmails: true,

      offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
      manuallySetAddress: true,
      'search-addressAutocomplete': addressAutocomplete,
      addressAutocomplete,
      coords,
      banId: '35288_7283_00001',
      locationLabel: 'Bureau',
      street: '3 rue de Valois',
      postalCode: '75001',
      city: 'Paris',
      latitude: '48.85332',
      longitude: '2.348979',
    }

    const result = setDefaultInitialValuesFromOffer({ offer: mockOffer })

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
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return all fields as read only when offer is pending', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PENDING,
    })

    const result = setFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return some fields as not read only when offer is synchronized', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Allocine' },
    })

    const result = setFormReadOnlyFields(offer)

    expect(result).not.toContain(['accessibility'])
  })
})
