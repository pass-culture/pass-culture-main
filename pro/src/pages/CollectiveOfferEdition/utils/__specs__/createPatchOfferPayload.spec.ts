import {
  EacFormat,
  PatchCollectiveOfferBodyModel,
  OfferAddressType,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

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
    participants: {
      ...buildStudentLevelsMapWithDefaultValue(true),
      all: false,
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
      all: true,
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
    venueId: venueId,
    offerVenue: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: 'TestOtherAddress update',
      venueId: venueId,
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
    const payload = createPatchOfferPayload({ ...offer }, initialValues)

    expect(payload).toMatchObject({
      ...patchOfferPayload,
      venueId: venueId,
    })
  })

  it('should return the correct patch offer payload for a template offer', () => {
    const payload = createPatchOfferTemplatePayload(
      { ...offer, priceDetail: '123', isTemplate: true },
      initialValues
    )

    expect(payload).toMatchObject({
      venueId: venueId,
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
      venueId: venueId,
      priceDetail: '123',
      dates: null,
    })
  })
})
