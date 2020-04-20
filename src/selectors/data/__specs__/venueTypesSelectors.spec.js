import { selectVenueTypes } from '../venueTypesSelectors'

describe('src | selectors | data | venuesSelectors', () => {
  describe('selectVenueTypes', () => {
    describe('when venue types attribute exists', () => {
      it('should return it', () => {
        // Given
        const store = {
          data: {
            "venue-types": [{ id: 1 }, { id: 2 }],
          },
        }

        // Then
        expect(selectVenueTypes(store)).toStrictEqual([{ id: 1 }, { id: 2 }])
      })
    })

    describe('when venue-types attribute does not not', () => {
      it('should return an empty array', () => {
        // Given
        const store = {
          data: {
          },
        }

        // Then
        expect(selectVenueTypes(store)).toStrictEqual([])
      })
    })
  })
})
