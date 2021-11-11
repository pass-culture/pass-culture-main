import { selectVenueTypes } from '../venueTypesSelectors'

describe('src | selectors | data | venuesSelectors', () => {
  describe('selectVenueTypes', () => {
    describe('when venue types attribute exists', () => {
      it('should return types ordered by label', () => {
        // Given
        const store = {
          data: {
            'venue-types': [
              { id: 1, label: 'Cinéma / Concert' },
              { id: 2, label: 'Autre' },
              { id: 3, label: 'Bibliothèque' },
            ],
          },
        }

        // When
        const venue_types = selectVenueTypes(store)

        // Then
        expect(venue_types).toStrictEqual([
          { id: 3, label: 'Bibliothèque' },
          { id: 1, label: 'Cinéma / Concert' },
          { id: 2, label: 'Autre' },
        ])
      })
    })

    describe('when venue-types attribute does not exist', () => {
      it('should return an empty array', () => {
        // Given
        const store = {
          data: {},
        }

        // When
        const venue_types = selectVenueTypes(store)

        // Then
        expect(venue_types).toStrictEqual([])
      })
    })
  })
})
