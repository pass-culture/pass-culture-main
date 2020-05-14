import { selectVenueLabels } from '../venueLabelsSelectors'

describe('src | selectors | data | venuesSelectors', () => {
  describe('selectVenueLabels', () => {
    describe('when venue labels attribute exists', () => {
      it('should return labels ordered by label', () => {
        // Given
        const store = {
          data: {
            'venue-labels': [
              { id: 1, label: "CNAREP - Centre national des arts de la rue et de l'espace public" },
              { id: 2, label: 'PNC - Pôle national du cirque' },
              { id: 3, label: 'Opéra national en région' },
            ],
          },
        }

        // When
        const venue_labels = selectVenueLabels(store)

        // Then
        expect(venue_labels).toStrictEqual([
          { id: 1, label: "CNAREP - Centre national des arts de la rue et de l'espace public" },
          { id: 3, label: 'Opéra national en région' },
          { id: 2, label: 'PNC - Pôle national du cirque' },
        ])
      })
    })

    describe('when venue-labels attribute does not exist', () => {
      it('should return an empty array', () => {
        // Given
        const store = {
          data: {},
        }

        // When
        const venue_labels = selectVenueLabels(store)

        // Then
        expect(venue_labels).toStrictEqual([])
      })
    })
  })
})
