import { DATE_FILTER } from '../../../components/pages/search/Filters/filtersEnums'
import {
  computeTimeRangeFromHoursToSeconds,
  TIMESTAMP,
} from '../../../components/pages/search/utils/date/time'
import { buildQueryOptions } from '../buildQueryOptions'
import { AppSearchFields } from '../constants'

const timestamp = TIMESTAMP
const computeTimeRange = computeTimeRangeFromHoursToSeconds

jest.mock('../../../components/pages/search/utils/date/time')

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
      timestamp.getFirstOfDate.mockReturnValue(123456789)
      timestamp.getLastOfDate.mockReturnValue(987654321)
      const selectedDate = new Date(2020, 3, 19, 11)

      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        date: {
          option: DATE_FILTER.USER_PICK.value,
          selectedDate,
        },
      })

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.prices]: { to: 1 } },
          { [AppSearchFields.dates]: { from: 123456789, to: 987654321 } },
        ],
      })
    })

    it('should fetch with price and time numericFilters', () => {
      computeTimeRange.mockReturnValue([123456789, 987654321])
      const timeRange = [10, 17]

      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        timeRange,
      })

      expect(computeTimeRange).toHaveBeenCalledWith(timeRange)
      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.prices]: { to: 1 } },
          { [AppSearchFields.times]: { from: 123456789, to: 987654321 } },
        ],
      })
    })

    it('should fetch with price, date and time numericFilters', () => {
      const timeRange = [18, 22]
      const selectedDate = new Date(2020, 3, 19, 11)
      timestamp.WEEK_END.getAllFromTimeRangeAndDate.mockReturnValue([
        [123456789, 987654321],
        [123, 1234],
      ])

      const filters = buildQueryOptions({
        ...baseParams,
        offerIsFree: true,
        date: {
          option: DATE_FILTER.CURRENT_WEEK_END.value,
          selectedDate,
        },
        timeRange,
      })

      expect(timestamp.WEEK_END.getAllFromTimeRangeAndDate).toHaveBeenCalledWith(
        selectedDate,
        timeRange
      )

      expect(filters.filters).toStrictEqual({
        all: [
          { [AppSearchFields.prices]: { to: 1 } },
          { [AppSearchFields.dates]: { from: 123456789, to: 987654321 } },
          { [AppSearchFields.dates]: { from: 123, to: 1234 } },
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
        current: 2,
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
})
