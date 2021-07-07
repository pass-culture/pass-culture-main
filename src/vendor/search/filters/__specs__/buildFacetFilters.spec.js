import { AppSearchFields } from '../../constants'
import { buildFacetFilters } from '../buildFacetFilters'

const baseParams = {
  offerTypes: {
    isDigital: false,
    isEvent: false,
    isThing: false,
  },
}

describe('buildFacetFilters', () => {
  describe('categories', () => {
    it('should fetch with no facetFilters parameter when no category is provided', () => {
      const offerCategories = []
      const filters = buildFacetFilters({ ...baseParams, offerCategories })
      expect(filters).toStrictEqual([])
    })

    it('should fetch with facetFilters parameter when one category is provided', () => {
      const offerCategories = ['LECON']
      const filters = buildFacetFilters({ ...baseParams, offerCategories })
      expect(filters).toStrictEqual([{ [AppSearchFields.category]: ['LECON'] }])
    })

    it('should fetch with facetFilters parameter when multiple categories are provided', () => {
      const offerCategories = ['SPECTACLE', 'LIVRE']
      const filters = buildFacetFilters({ ...baseParams, offerCategories })
      expect(filters).toStrictEqual([{ [AppSearchFields.category]: ['SPECTACLE', 'LIVRE'] }])
    })
  })

  describe('offer types', () => {
    it('should fetch with no facetFilters when no offer type is provided', () => {
      const offerTypes = {
        isDigital: false,
        isEvent: false,
        isThing: false,
      }
      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([])
    })

    it('should fetch with facetFilters when offer is digital', () => {
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: false,
      }
      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([{ [AppSearchFields.is_digital]: 1 }])
    })

    it('should fetch with facetFilters when offer is physical only', () => {
      const offerTypes = {
        isDigital: false,
        isEvent: false,
        isThing: true,
      }
      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([
        { [AppSearchFields.is_digital]: 0 },
        { [AppSearchFields.is_thing]: 1 },
      ])
    })

    it('should fetch with facetFilters when offer is event only', () => {
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([{ [AppSearchFields.is_event]: 1 }])
    })

    it('should fetch with facetFilters when offer is digital and physical', () => {
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: true,
      }

      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([{ [AppSearchFields.is_thing]: 1 }])
    })

    it('should fetch with facetFilters when offer is digital or an event', () => {
      const offerTypes = {
        isDigital: true,
        isEvent: true,
        isThing: false,
      }

      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([
        { [AppSearchFields.is_digital]: 1 },
        { [AppSearchFields.is_event]: 1 },
      ])
    })

    it('should fetch with facetFilters when offer is physical or an event', () => {
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: true,
      }

      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([{ [AppSearchFields.is_digital]: 0 }])
    })

    it('should fetch with no facetFilters when offer is digital, event and thing', () => {
      const offerTypes = {
        isDigital: true,
        isEvent: true,
        isThing: true,
      }

      const filters = buildFacetFilters({ offerTypes })
      expect(filters).toStrictEqual([])
    })
  })

  describe('offer duo', () => {
    it('should fetch with no facetFilters when offer duo is false', () => {
      const filters = buildFacetFilters({ ...baseParams, offerIsDuo: false })
      expect(filters).toStrictEqual([])
    })

    it('should fetch with facetFilters when offer duo is true', () => {
      const filters = buildFacetFilters({ ...baseParams, offerIsDuo: true })
      expect(filters).toStrictEqual([{ [AppSearchFields.is_duo]: 1 }])
    })
  })

  describe('tags', () => {
    it('should fetch with no facetFilters parameter when no tags are provided', () => {
      const tags = []
      const filters = buildFacetFilters({ ...baseParams, tags })
      expect(filters).toStrictEqual([])
    })

    it('should fetch with facetFilters parameter when tags are provided', () => {
      const tags = ['Semaine du 14 juillet', 'Offre cinema spéciale pass culture']
      const filters = buildFacetFilters({ ...baseParams, tags })
      expect(filters).toStrictEqual([
        { [AppSearchFields.tags]: ['Semaine du 14 juillet', 'Offre cinema spéciale pass culture'] },
      ])
    })
  })
})
