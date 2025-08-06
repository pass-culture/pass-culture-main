import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'

import { applyVenueDefaultsToFormValues } from '../applyVenueDefaultsToFormValues'

describe('applyVenueDefaultsToFormValues', () => {
  it('should return the initial values if the venue cant be found', () => {
    const formValues = { ...getDefaultEducationalValues(), venueId: '2' }
    const newFormValues = applyVenueDefaultsToFormValues(
      formValues,
      {
        id: 1,
        managedVenues: [],
        name: 'test',
        allowedOnAdage: true,
      },
      false
    )

    expect(newFormValues).toEqual(formValues)
  })

  it('should return the accessibility values from the venue', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      { ...getDefaultEducationalValues(), venueId: '2', offererId: '1' },
      {
        id: 1,
        managedVenues: [
          {
            id: 2,
            isVirtual: true,
            name: 'test',
            audioDisabilityCompliant: true,
            mentalDisabilityCompliant: true,
          },
        ],
        name: 'test',
        allowedOnAdage: true,
      },
      false
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
      {
        id: 1,
        managedVenues: [
          {
            id: 2,
            isVirtual: true,
            name: 'test',
          },
        ],
        name: 'test',
        allowedOnAdage: true,
      },
      false
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
      {
        id: 1,
        managedVenues: [
          {
            id: 2,
            isVirtual: true,
            name: 'test',
            collectiveEmail: 'test@email.co',
            collectivePhone: '00000000',
          },
        ],
        name: 'test',
        allowedOnAdage: true,
      },
      true
    )

    expect(newFormValues.email).toEqual('test@email.co')
    expect(newFormValues.phone).toEqual('00000000')
  })

  it('should not prefill the form values with the venue email and phone if they already exist on in the form', () => {
    const newFormValues = applyVenueDefaultsToFormValues(
      {
        ...getDefaultEducationalValues(),
        offererId: '1',
        venueId: '2',
        email: 'test2@email.co',
        phone: '11111111',
      },
      {
        id: 1,
        managedVenues: [
          {
            id: 2,
            isVirtual: true,
            name: 'test',
            collectiveEmail: 'test@email.co',
            collectivePhone: '00000000',
          },
        ],
        name: 'test',
        allowedOnAdage: true,
      },
      true
    )

    expect(newFormValues.email).toEqual('test2@email.co')
    expect(newFormValues.phone).toEqual('11111111')
  })
})
