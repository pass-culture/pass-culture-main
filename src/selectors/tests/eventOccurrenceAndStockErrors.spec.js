import eventOccurrenceAndStocksErrorsSelector from '../eventOccurrenceAndStockErrors'

describe('eventOccurrenceAndStocksErrorsSelector', () => {
  describe('With eventOccurrenceIdOrNew', () => {
    it('should select errors corresponding to eventOccurrenceId key', () => {
      // Given
      const state = {
        errors: {
          eventOccurrenceKA: null,
          stockJ4: {
            available: [
              'la quantité pour cette offre ne peut pas être inférieure au nombre de réservations existantes.',
            ],
          },
        },
      }
      const eventOccurrenceIdOrNew = 'J4'
      const stockIdOrNew = 'MY'

      // When
      const result = eventOccurrenceAndStocksErrorsSelector(
        state,
        eventOccurrenceIdOrNew,
        stockIdOrNew
      )
      const expected = {
        Places: [
          'la quantité pour cette offre ne peut pas être inférieure au nombre de réservations existantes.',
        ],
      }

      // Then
      expect(result).toEqual(expected)
    })
  })
  describe('With stockIdOrNew', () => {
    it('should select errors corresponding to stockIdOrNew key', () => {
      // Given
      const state = {
        errors: {
          eventOccurrenceKA: null,
          stockNA: {
            available: [
              'la quantité pour cette offre ne peut pas être inférieure au nombre de réservations existantes.',
            ],
          },
        },
      }
      const eventOccurrenceIdOrNew = undefined
      const stockIdOrNew = 'NA'

      // When'
      const result = eventOccurrenceAndStocksErrorsSelector(
        state,
        eventOccurrenceIdOrNew,
        stockIdOrNew
      )
      const expected = {
        Places: [
          'la quantité pour cette offre ne peut pas être inférieure au nombre de réservations existantes.',
        ],
      }

      // Then
      expect(result).toEqual(expected)
    })
  })
})
