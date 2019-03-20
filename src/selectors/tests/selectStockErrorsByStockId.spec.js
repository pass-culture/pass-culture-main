import selectStockErrorsByStockId from '../selectStockErrorsByStockId'

describe('selectStockErrorsByStockId', () => {
  describe('With stockIdOrNew', () => {
    it('should select errors corresponding to stockIdOrNew key', () => {
      // Given
      const state = {
        errors: {
          stockNA: {
            available: [
              'la quantité pour cette offre ne peut pas être inférieure au nombre de réservations existantes.',
            ],
          },
        },
      }
      const stockIdOrNew = 'NA'

      // When'
      const result = selectStockErrorsByStockId(state, stockIdOrNew)
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
