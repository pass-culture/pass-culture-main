import { PatchCollectiveOfferBodyModel, SubcategoryIdEnum } from 'apiClient/v1'
import { OfferAddressType } from 'apiClient/v2'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

import { createPatchOfferPayload } from '../createPatchOfferPayload'

describe('createPatchOfferPayload', () => {
  const initialValues: IOfferEducationalFormValues = {
    title: 'Test Offer',
    description: 'Test Description',
    offererId: 'DY',
    category: 'CINEMA',
    duration: '1:30',
    subCategory: SubcategoryIdEnum.ABO_JEU_VIDEO,
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
      venueId: 'KM',
    },
    participants: {
      ...buildStudentLevelsMapWithDefaultValue(true),
      all: false,
    },
    phone: '0123456789',
    email: 'test@email.com',
    domains: [],
    interventionArea: ['2A'],
  }
  const offer: IOfferEducationalFormValues = {
    title: 'Test Offer update',
    description: 'Test Description update',
    offererId: 'DY',
    category: 'JEUX',
    duration: '2:00',
    subCategory: SubcategoryIdEnum.ABO_CONCERT,
    accessibility: {
      mental: false,
      motor: true,
      audio: false,
      visual: true,
      none: true,
    },
    notificationEmails: ['test3@email.com', 'test4@email.com'],
    venueId: 'KC',
    eventAddress: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: 'TestOtherAddress update',
      venueId: 'KC',
    },
    participants: {
      ...buildStudentLevelsMapWithDefaultValue(false),
      all: true,
    },
    phone: '0123456788',
    email: 'test2@email.com',
    domains: ['123'],
    interventionArea: ['2B'],
  }

  const patchOfferPayload: PatchCollectiveOfferBodyModel = {
    name: 'Test Offer update',
    description: 'Test Description update',
    durationMinutes: 120,
    subcategoryId: SubcategoryIdEnum.ABO_CONCERT,
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: false,
    visualDisabilityCompliant: true,
    bookingEmails: ['test3@email.com', 'test4@email.com'],
    venueId: 12,
    offerVenue: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: 'TestOtherAddress update',
      // @ts-expect-error api expect number
      venueId: 15,
    },
    students: [],
    contactPhone: '0123456788',
    contactEmail: 'test2@email.com',
    interventionArea: ['2B'],
    domains: [123],
  }

  it('should return the correct patch offer payload for a non-template offer', () => {
    const payload = createPatchOfferPayload({ ...offer }, initialValues, false)

    expect(payload).toMatchObject(patchOfferPayload)
  })

  it('should return the correct patch offer payload for a template offer', () => {
    const payload = createPatchOfferPayload(
      { ...offer, priceDetail: '123' },
      initialValues,
      true
    )

    expect(payload).toMatchObject({
      venueId: 'KC',
      priceDetail: '123',
    })
  })
})
