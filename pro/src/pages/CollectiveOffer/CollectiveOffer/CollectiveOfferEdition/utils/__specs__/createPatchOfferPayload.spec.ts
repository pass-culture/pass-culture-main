import {
  EacFormat,
  PatchCollectiveOfferBodyModel,
  OfferAddressType,
  CollectiveLocationType,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { buildStudentLevelsMapWithDefaultValue } from 'commons/core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

import {
  createPatchOfferPayload,
  createPatchOfferTemplatePayload,
} from '../createPatchOfferPayload'

describe('createPatchOfferPayload', () => {
  const offerId = '17'
  const venueId = 12

  const initialValues: OfferEducationalFormValues = {
    title: 'Test Offer',
    description: 'Test Description',
    offererId: 'DY',
    duration: '1:30',
    accessibility: {
      mental: true,
      motor: false,
      audio: true,
      visual: false,
      none: false,
    },
    notificationEmails: ['test1@email.com', 'test2@email.com'],
    venueId: 'KM',
    eventAddress: {
      addressType: OfferAddressType.OFFERER_VENUE,
      otherAddress: 'TestOtherAddress',
      venueId: 12,
    },
    city: 'Paris',
    latitude: '3',
    longitude: '2',
    postalCode: '75018',
    street: 'rue de la paix',
    location: {
      locationType: CollectiveLocationType.ADDRESS,
      address: {
        isVenueAddress: true,
        isManualEdition: false,
        label: '',
        id_oa: '123',
      },
    },
    participants: {
      ...buildStudentLevelsMapWithDefaultValue(true),
      college: false,
      lycee: false,
      marseille: false,
    },
    phone: '0123456789',
    email: 'test@email.com',
    domains: [],
    interventionArea: ['2A'],
    beginningDate: '2021-09-01',
    endingDate: '2021-09-30',
    datesType: 'specific_dates',
    hour: '10:00',
    isTemplate: false,
    formats: [EacFormat.CONCERT],
    'search-addressAutocomplete': '',
    addressAutocomplete: '',
  }

  const offer: OfferEducationalFormValues = {
    title: 'Test Offer update',
    description: 'Test Description update',
    offererId: offerId,
    duration: '2:00',
    accessibility: {
      mental: false,
      motor: true,
      audio: false,
      visual: true,
      none: true,
    },
    notificationEmails: ['test3@email.com', 'test4@email.com'],
    venueId: venueId.toString(),
    eventAddress: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: 'TestOtherAddress update',
      venueId: 12,
    },
    participants: {
      ...buildStudentLevelsMapWithDefaultValue(false),
      college: false,
      lycee: false,
      marseille: false,
    },
    phone: '0123456788',
    email: 'test2@email.com',
    domains: ['123'],
    interventionArea: ['2B'],
    nationalProgramId: '1',
    beginningDate: '2021-09-01',
    endingDate: '2021-09-30',
    datesType: 'specific_dates',
    hour: '10:00',
    isTemplate: false,
    formats: [EacFormat.ATELIER_DE_PRATIQUE],
    'search-addressAutocomplete': '',
    addressAutocomplete: '',
    city: 'Marseille',
    latitude: '3',
    longitude: '2',
    postalCode: '13007',
    street: 'rue de la paix',
    location: {
      locationType: CollectiveLocationType.ADDRESS,
      address: {
        isVenueAddress: false,
        id_oa: 'SPECIFIC_ADDRESS',
        isManualEdition: false,
        label: 'Une autre adresse',
      },
    },
  }

  const patchOfferPayload: PatchCollectiveOfferBodyModel = {
    name: 'Test Offer update',
    description: 'Test Description update',
    durationMinutes: 120,
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: false,
    visualDisabilityCompliant: true,
    bookingEmails: ['test3@email.com', 'test4@email.com'],
    venueId,
    offerVenue: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: 'TestOtherAddress update',
      venueId,
    },
    students: [],
    contactPhone: '0123456788',
    contactEmail: 'test2@email.com',
    interventionArea: ['2B'],
    domains: [123],
    nationalProgramId: 1,
    formats: [EacFormat.ATELIER_DE_PRATIQUE],
  }

  it('should return the correct patch offer payload for a non-template offer', () => {
    const payload = createPatchOfferPayload({ ...offer }, initialValues, false)

    expect(payload).toMatchObject({
      ...patchOfferPayload,
      venueId,
    })
  })

  it('should return the correct patch offer payload for a template offer', () => {
    const payload = createPatchOfferTemplatePayload(
      { ...offer, priceDetail: '123', isTemplate: true },
      initialValues,
      false
    )

    expect(payload).toMatchObject({
      venueId,
      priceDetail: '123',
    })
  })

  it('should return the correct patch offer payload for a template offer when dates are empty', () => {
    const payload = createPatchOfferTemplatePayload(
      {
        ...offer,
        priceDetail: '123',
        isTemplate: true,
        beginningDate: '',
        datesType: 'permanent',
      },
      initialValues,
      false
    )

    expect(payload).toMatchObject({
      venueId,
      priceDetail: '123',
      dates: null,
    })
  })

  it('should return patch offer payload with location key when OA FF is active', () => {
    const payload = createPatchOfferPayload(offer, initialValues, true)

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          address: {
            city: 'Marseille',
            latitude: '3',
            longitude: '2',
            postalCode: '13007',
            street: 'rue de la paix',
            isVenueAddress: false,
            label: 'Une autre adresse',
            isManualEdition: false,
            banId: '',
            coords: '',
          },
        },
      })
    )
  })

  it('should return patch offer payload with offerVenue key when OA FF is inactive', () => {
    const payload = createPatchOfferPayload(offer, initialValues, false)

    expect(payload).toEqual(
      expect.objectContaining({
        offerVenue: {
          addressType: 'school',
          otherAddress: 'TestOtherAddress update',
          venueId: 12,
        },
      })
    )
  })
})
