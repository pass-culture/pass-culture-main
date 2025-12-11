import { makeVenueListItem } from '../factories/individualApiFactories'
import { withVenueHelpers } from '../withVenueHelpers'

describe('withVenueHelpers', () => {
  const baseAddress = {
    id: 1,
    id_oa: 1,
    latitude: 1.23,
    longitude: 4.56,
    isManualEdition: false,
  }

  describe('fullAddressAsString', () => {
    it('should return null when address is nullish', () => {
      const venue = makeVenueListItem({ id: 1, address: null })

      const venueWithHelpers = withVenueHelpers(venue)

      expect(venueWithHelpers.fullAddressAsString).toBeNull()
    })

    it('should return full address with street when street is provided', () => {
      const venue = makeVenueListItem({
        id: 1,
        address: {
          ...baseAddress,
          street: '123 Rue de Rivoli',
          postalCode: '75001',
          city: 'Paris',
        },
      })

      const venueWithHelpers = withVenueHelpers(venue)

      expect(venueWithHelpers.fullAddressAsString).toBe(
        '123 Rue de Rivoli, 75001 Paris'
      )
    })

    it('should return address without street when street is nullish', () => {
      const venue = makeVenueListItem({
        id: 1,
        address: {
          ...baseAddress,
          street: null,
          postalCode: '75001',
          city: 'Paris',
        },
      })

      const venueWithHelpers = withVenueHelpers(venue)

      expect(venueWithHelpers.fullAddressAsString).toBe('75001 Paris')
    })
  })
})
