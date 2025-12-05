import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import { serializeEditVenueBodyModel } from '../serializers'
import { setInitialFormValues } from '../setInitialFormValues'

describe('Venue edition payload serializer', () => {
  it('should return an empty payload when nothing changed', () => {
    const initialFormValues = setInitialFormValues(defaultGetVenue)

    expect(
      serializeEditVenueBodyModel(
        initialFormValues,
        initialFormValues,
        true,
        false
      )
    ).toEqual({})
  })

  it('should serialize newly added opening hours', () => {
    const initialFormValues = setInitialFormValues({
      ...defaultGetVenue,
      openingHours: null,
    })
    const updatedFormValues = {
      ...initialFormValues,
      openingHours: {
        MONDAY: [
          ['01:00', '09:00'],
          ['10:00', '11:00'],
        ],
      },
    }

    expect(
      serializeEditVenueBodyModel(
        updatedFormValues,
        initialFormValues,
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
    const initialFormValues = setInitialFormValues({
      ...defaultGetVenue,
      openingHours: {
        MONDAY: [['08:00', '12:00']],
      },
    })
    const updatedFormValues = {
      ...initialFormValues,
      openingHours: null,
    }

    expect(
      serializeEditVenueBodyModel(
        updatedFormValues,
        initialFormValues,
        true,
        true
      )
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
})
