import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'

import { serializeEditVenueBodyModel } from '../serializers'
import { setInitialFormValues } from '../setInitialFormValues'

describe('Venue edition payload serializer', () => {
  it('should serialize a venue payload with no openingHours', () => {
    const initialFormValues = setInitialFormValues({
      ...defaultGetVenue,
      openingHours: null,
    })
    expect(serializeEditVenueBodyModel(initialFormValues, true, false)).toEqual(
      expect.objectContaining({ openingHours: null })
    )
  })

  it('should serialize a venue payload with openingHours', () => {
    const initialFormValues = setInitialFormValues({
      ...defaultGetVenue,
      openingHours: {
        MONDAY: [
          { open: '01:00', close: '09:00' },
          { open: '10:00', close: '11:00' },
        ],
      },
    })
    expect(serializeEditVenueBodyModel(initialFormValues, true, false)).toEqual(
      expect.objectContaining({
        openingHours: expect.objectContaining(
          {
            'MONDAY': [['01:00', '09:00'], ['10:00', '11:00']],
          },
        ),
      })
    )
  })

  it('should serialize a venue payload with no opening hours and that has never had opening hours before', () => {
    const initialFormValues = setInitialFormValues({
      ...defaultGetVenue,
      openingHours: null,
    })
    expect(serializeEditVenueBodyModel(initialFormValues, true, true)).toEqual(
      expect.objectContaining({ openingHours: {} }),
    )
  })
})
