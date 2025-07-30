import { SubcategoryIdEnum } from 'apiClient/v1'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'

import { MOCK_SUB_CATEGORIES, MOCK_SUB_CATEGORY } from '../__mocks__/constants'
import { isOfferSubcategoryOnline } from '../utils'

describe('isOfferSubcategoryOnline', () => {
  // --- Test Group 1: Offer has a URL ---
  // The function should prioritize the `url` property over the subcategory status.
  describe('when the offer has a URL', () => {
    it('should return true if the offer has a valid, non-empty URL', () => {
      const offer = getIndividualOfferFactory({ url: 'https://example.com' })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(true)
    })

    it('should return true if the URL has whitespace that can be trimmed', () => {
      const offer = getIndividualOfferFactory({
        url: '  https://example.com  ',
      })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(true)
    })
  })

  // --- Test Group 2: Offer does NOT have a URL ---
  // The function should fall back to checking the subcategory's platform.
  describe('when the offer does not have a URL', () => {
    it('should return true if the corresponding subcategory is ONLINE', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: MOCK_SUB_CATEGORY.EVENT_ONLINE.id,
        url: null,
      })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(true)
    })

    it('should return false if the corresponding subcategory is OFFLINE', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: MOCK_SUB_CATEGORY.EVENT_OFFLINE.id,
        url: '',
      }) // Test with empty string

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(false)
    })

    it('should return false if the corresponding subcategory is not explicitly ONLINE', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: MOCK_SUB_CATEGORY.EVENT_ONLINE_AND_OFFLINE.id,
        url: null,
      })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(false)
    })

    it('should return false if the URL contains only whitespace', () => {
      // A URL with only spaces becomes an empty string after trim(), so `hasUrl` is false.
      const offer = getIndividualOfferFactory({
        subcategoryId: MOCK_SUB_CATEGORY.EVENT_OFFLINE.id,
        url: '   ',
      })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(false)
    })

    it('should return false if the subcategoryId does not match any subcategory', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: 'A_NONEXISTENT_SUCATEGORY' as SubcategoryIdEnum,
        url: null,
      })

      const result = isOfferSubcategoryOnline(offer, MOCK_SUB_CATEGORIES)

      expect(result).toBe(false)
    })

    it('should return false if the subcategories array is empty', () => {
      const offer = getIndividualOfferFactory({
        subcategoryId: 'A_NONEXISTENT_SUCATEGORY' as SubcategoryIdEnum,
        url: null,
      })

      const result = isOfferSubcategoryOnline(offer, [])

      expect(result).toBe(false)
    })
  })
})
