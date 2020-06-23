import { sortByOfferName } from '../sortingFunctions'

describe('utils | sortingFunctions', () => {
  describe('sortByOfferName', () => {
    it('should return 1 when first row offer name comes after second row offer name', () => {
      // given
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Zebre du Bengal'
          }
        }
      }
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant'
          }
        }
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(1)
    })

    it('should return -1 when first row offer name comes before second row offer name', () => {
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant'
          }
        }
      }
      // given
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Zebre du Bengal'
          }
        }
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(-1)
    })

    it('should return 0 when first row offer name is the same as second row offer name', () => {
      const firstRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant'
          }
        }
      }
      // given
      const secondRow = {
        original: {
          stock: {
            offer_name: 'Babar, mon ami éléphant'
          }
        }
      }

      // when
      const result = sortByOfferName(firstRow, secondRow)

      // then
      expect(result).toBe(0)
    })
  })
})
