import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { applyVenueDefaultsToFormValues } from '../applyVenueDefaultsToFormValues'

describe('applyVenueDefaultsToFormValues', () => {
  it('should return the accessibility values from the venue', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      { ...getDefaultEducationalValues(), venueId: '2', offererId: '1' },
      false,
      makeGetVenueResponseModel({
        id: 2,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
      })
    )

    expect(newFormValues).toEqual(
      expect.objectContaining({
        accessibility: {
          audio: true,
          mental: true,
          motor: false,
          none: false,
          visual: false,
        },
      })
    )
  })

  it('should set disability compliance to none if no accessibility value is checked on the venue', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      { ...getDefaultEducationalValues(), venueId: '2', offererId: '1' },
      false,
      makeGetVenueResponseModel({
        id: 2,
        audioDisabilityCompliant: null,
        mentalDisabilityCompliant: null,
        motorDisabilityCompliant: null,
        visualDisabilityCompliant: null,
      })
    )

    expect(newFormValues).toEqual(
      expect.objectContaining({
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: true,
          visual: false,
        },
      })
    )
  })

  it('should prefill the form values with the venue email and phone if the venue has them', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      { ...getDefaultEducationalValues(), offererId: '1', venueId: '2' },
      true,
      makeGetVenueResponseModel({
        id: 2,
        collectiveEmail: 'test@email.co',
        collectivePhone: '00000000',
      })
    )

    expect(newFormValues.contactEmail).toEqual('test@email.co')
    expect(newFormValues.phone).toEqual('00000000')
  })

  it('should not prefill the form values with the venue email and phone if they already exist on in the form', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      {
        ...getDefaultEducationalValues(),
        offererId: '1',
        venueId: '2',
        contactEmail: 'test2@email.co',
        phone: '11111111',
      },
      true,
      makeGetVenueResponseModel({
        id: 2,
        collectiveEmail: 'test@email.co',
        collectivePhone: '00000000',
      })
    )

    expect(newFormValues.contactEmail).toEqual('test2@email.co')
    expect(newFormValues.phone).toEqual('11111111')
  })
})
