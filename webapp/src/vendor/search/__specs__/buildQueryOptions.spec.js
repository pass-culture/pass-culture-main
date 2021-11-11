import { DATE_FILTER } from '../../../components/pages/search/Filters/filtersEnums'
import { buildQueryOptions } from '../buildQueryOptions'
import { AppSearchFields } from '../constants'

const HOUR = 60 * 60

const baseParams = {
  offerTypes: {
    isDigital: false,
    isEvent: false,
    isThing: false,
  },
}

describe('buildQueryOptions', () => {
  describe('multiple parameters', () => {
    it('should fetch with price and date numericFilters', () => {
      const selectedDate = new Date(2020, 3, 19, 11)
      const from = '2020-04-19T00:00:00.000Z'
      const to = '2020-04-19T23:59:59.000Z'

      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        date: {
          option: DATE_FILTER.USER_PICK.value,
          selectedDate,
        },
      })

      expect(filters.filters).toStrictEqual({
        all: [{ [AppSearchFields.prices]: { to: 1 } }, { [AppSearchFields.dates]: { from, to } }],
      })
    })

    it('should fetch with price and time numericFilters', () => {
      const timeRange = [10, 17]
      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        timeRange,
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.prices]: { to: 1 } },
          { [AppSearchFields.times]: { from: 10 * HOUR, to: 17 * HOUR } },
        ],
      })
    })

    it('should fetch with price, date and time numericFilters', () => {
      const selectedDate = new Date(2020, 3, 19, 11)
      const timeRange = [18, 22]
      const sundayFrom = '2020-04-19T18:00:00.000Z'
      const sundayTo = '2020-04-19T22:00:00.000Z'

      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        date: {
          option: DATE_FILTER.CURRENT_WEEK_END.value,
          selectedDate,
        },
        timeRange,
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.prices]: { to: 1 } },
          { [AppSearchFields.dates]: { from: sundayFrom, to: sundayTo } },
        ],
      })
    })

    it('should fetch with all given search parameters', () => {
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const offerCategories = ['LECON', 'VISITE']
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: false,
      }
      const page = 2

      const filters = buildQueryOptions(
        {
          aroundRadius: 123,
          offerTypes,
          offerCategories,
          geolocation,
          searchAround: false,
        },
        page
      )

      expect(filters.page).toStrictEqual({
        current: 3,
        size: 20,
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.is_digital]: 1 },
          { [AppSearchFields.category]: ['LECON', 'VISITE'] },
          { [AppSearchFields.prices]: { to: 30000 } },
        ],
      })
    })

    it('should fetch event offers for categories pratique & spectacle around me', () => {
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const offerCategories = ['PRATIQUE', 'SPECTACLE']
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      const filters = buildQueryOptions({
        aroundRadius: 123,
        offerTypes,
        offerCategories,
        geolocation,
        offerIsDuo: false,
        searchAround: true,
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.is_event]: 1 },
          { [AppSearchFields.category]: ['PRATIQUE', 'SPECTACLE'] },
          { [AppSearchFields.prices]: { to: 30000 } },
          { [AppSearchFields.venue_position]: { center: '42, 43', distance: 123, unit: 'km' } },
        ],
      })
    })

    it('should fetch duo & free event offers for categories pratique & spectacle around me', () => {
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const offerCategories = ['PRATIQUE', 'SPECTACLE']
      const priceRange = [5, 40]
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      const filters = buildQueryOptions({
        aroundRadius: 123,
        offerTypes,
        offerCategories,
        geolocation,
        offerIsDuo: true,
        priceRange,
        searchAround: true,
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.is_event]: 1 },
          { [AppSearchFields.category]: ['PRATIQUE', 'SPECTACLE'] },
          { [AppSearchFields.is_duo]: 1 },
          { [AppSearchFields.prices]: { from: 500, to: 4000 } },
          { [AppSearchFields.venue_position]: { center: '42, 43', distance: 123, unit: 'km' } },
        ],
      })
    })
  })

  describe('hitsPerPage', () => {
    it('should fetch with no hitsPerPage parameter when not provided', () => {
      const filters = buildQueryOptions({ ...baseParams, hitsPerPage: null })
      expect(filters.page).toStrictEqual({
        current: 1,
        size: 20,
      })
    })

    it('should fetch with hitsPerPage when provided', () => {
      const filters = buildQueryOptions({ ...baseParams, hitsPerPage: 5 })
      expect(filters.page).toStrictEqual({
        current: 1,
        size: 5,
      })
    })
  })

  describe('group', () => {
    it('should always fetch a single offer per group (isbn/visa/...)', () => {
      const filters = buildQueryOptions(baseParams)
      expect(filters.group).toStrictEqual({ field: AppSearchFields.group })
    })
  })
})
