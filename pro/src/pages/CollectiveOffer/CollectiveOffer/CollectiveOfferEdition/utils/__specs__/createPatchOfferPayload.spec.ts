import {
  CollectiveLocationType,
  EacFormat,
  type PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { buildStudentLevelsMapWithDefaultValue } from '@/commons/core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

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
    notificationEmails: [
      { email: 'test1@email.com' },
      { email: 'test2@email.com' },
    ],
    venueId: 'KM',
    city: 'Paris',
    latitude: '3',
    longitude: '2',
    postalCode: '75018',
    street: 'rue de la paix',
    location: {
      locationType: CollectiveLocationType.ADDRESS,
      location: {
        isVenueLocation: true,
        isManualEdition: false,
        label: '',
        id: '123',
      },
    },
    participants: buildStudentLevelsMapWithDefaultValue(true),
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
    notificationEmails: [
      { email: 'test3@email.com' },
      { email: 'test4@email.com' },
    ],
    venueId: venueId.toString(),
    participants: buildStudentLevelsMapWithDefaultValue(false),
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
      location: {
        isVenueLocation: false,
        id: 'SPECIFIC_ADDRESS',
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
    students: [],
    contactPhone: '0123456788',
    contactEmail: 'test2@email.com',
    interventionArea: ['2B'],
    domains: [123],
    nationalProgramId: 1,
    formats: [EacFormat.ATELIER_DE_PRATIQUE],
  }

  it('should return the correct patch offer payload for a non-template offer', () => {
    const payload = createPatchOfferPayload({ ...offer }, initialValues)

    expect(payload).toMatchObject({
      ...patchOfferPayload,
      venueId,
    })
  })

  it('should return the correct patch offer payload for a template offer', () => {
    const payload = createPatchOfferTemplatePayload(
      { ...offer, priceDetail: '123', isTemplate: true },
      initialValues
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
      initialValues
    )

    expect(payload).toMatchObject({
      venueId,
      priceDetail: '123',
      dates: null,
    })
  })

  it('should return patch offer payload with location key', () => {
    const payload = createPatchOfferPayload(offer, initialValues)

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            city: 'Marseille',
            latitude: '3',
            longitude: '2',
            postalCode: '13007',
            street: 'rue de la paix',
            isVenueLocation: false,
            label: 'Une autre adresse',
            isManualEdition: false,
            banId: '',
            coords: '',
          },
        },
      })
    )
  })

  it('should return patch offer payload with minimal location key for isVenueLocation', () => {
    const offerAtVenueLocation = {
      ...offer,
      location: { ...offer.location, location: { isVenueLocation: true } },
    }
    const payload = createPatchOfferPayload(offerAtVenueLocation, initialValues)

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            isVenueLocation: true,
          },
        },
      })
    )
  })

  it('should return patch offer payload with location key when city has changed', () => {
    const payload = createPatchOfferPayload(
      { ...offer, city: 'Paris' },
      initialValues
    )

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            city: 'Paris',
            latitude: '3',
            longitude: '2',
            postalCode: '13007',
            street: 'rue de la paix',
            isVenueLocation: false,
            label: 'Une autre adresse',
            isManualEdition: false,
            banId: '',
            coords: '',
          },
        },
      })
    )
  })

  it('should return patch offer payload with location key when locationType is SCHOOL', () => {
    const payload = createPatchOfferPayload(
      {
        ...offer,
        location: {
          locationType: CollectiveLocationType.SCHOOL,
          location: {
            isManualEdition: false,
            isVenueLocation: false,
            label: '',
          },
        },
      },
      initialValues
    )

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.SCHOOL,
        },
      })
    )
  })

  it('should return patch offer payload with location key when locationType is TO_BE_DEFINED', () => {
    const payload = createPatchOfferPayload(
      {
        ...offer,
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          location: {
            isManualEdition: false,
            isVenueLocation: false,
            label: '',
          },
          locationComment: 'toto',
        },
      },
      initialValues
    )

    expect(payload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: 'toto',
        },
      })
    )
  })
})
