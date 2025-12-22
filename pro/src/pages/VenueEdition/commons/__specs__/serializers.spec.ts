import type { VenueEditionFormValues } from '@/pages/VenueEdition/commons/types'

import { serializeEditVenueBodyModel } from '../serializers'

describe('Venue edition payload serializer', () => {
  it('should return an empty payload when nothing changed', () => {
    expect(
      serializeEditVenueBodyModel(
        {} as Partial<VenueEditionFormValues>,
        true,
        false
      )
    ).toEqual({})
  })

  it('should serialize newly added opening hours', () => {
    expect(
      serializeEditVenueBodyModel(
        {
          openingHours: {
            MONDAY: [
              ['01:00', '09:00'],
              ['10:00', '11:00'],
            ],
          },
        },
        true,
        false
      )
    ).toEqual({
      openingHours: expect.objectContaining({
        MONDAY: [
          ['01:00', '09:00'],
          ['10:00', '11:00'],
        ],
      }),
    })
  })

  it('should serialize cleaned opening hours when hours are removed', () => {
    expect(
      serializeEditVenueBodyModel({ openingHours: null }, true, true)
    ).toEqual({
      openingHours: {
        MONDAY: null,
        TUESDAY: null,
        WEDNESDAY: null,
        THURSDAY: null,
        FRIDAY: null,
        SATURDAY: null,
        SUNDAY: null,
      },
    })
  })

  it('should not serialize opening hours if undefined', () => {
    expect(
      serializeEditVenueBodyModel({ openingHours: undefined }, true, true)
    ).toEqual({})
  })

  it('should not serialize contact form if no contact is set', () => {
    expect(
      serializeEditVenueBodyModel(
        { email: null, phoneNumber: null, webSite: null },
        false,
        false
      )
    ).toEqual({})
  })

  it('should serialize contact form if any contact is set', () => {
    expect(
      serializeEditVenueBodyModel({ email: 'email' }, false, false)
    ).toEqual({
      contact: {
        email: 'email',
        phoneNumber: null,
        socialMedias: null,
        website: null,
      },
    })
  })
})
