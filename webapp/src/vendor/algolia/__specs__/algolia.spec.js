import algoliasearch from 'algoliasearch'
import {
  computeTimeRangeFromHoursToSeconds,
  TIMESTAMP,
} from '../../../components/pages/search/utils/date/time'
import {
  ALGOLIA_APPLICATION_ID,
  ALGOLIA_INDEX_NAME,
  ALGOLIA_SEARCH_API_KEY,
} from '../../../utils/config'
import { fetchAlgolia } from '../algolia'

jest.mock('algoliasearch')
jest.mock('../../../utils/config', () => ({
  ALGOLIA_APPLICATION_ID: 'appId',
  ALGOLIA_INDEX_NAME: 'indexName',
  ALGOLIA_SEARCH_API_KEY: 'apiKey',
}))
jest.mock('../../../components/pages/search/utils/date/time', () => ({
  TIMESTAMP: {
    getLastOfDate: jest.fn(),
    getFromDate: jest.fn(),
    getFirstOfDate: jest.fn(),
    getAllFromTimeRangeAndDate: jest.fn(),
    WEEK_END: {
      getFirstFromDate: jest.fn(),
      getAllFromTimeRangeAndDate: jest.fn(),
    },
    WEEK: {
      getLastFromDate: jest.fn(),
      getAllFromTimeRangeAndDate: jest.fn(),
    },
  },
  computeTimeRangeFromHoursToSeconds: jest.fn(),
}))

describe('fetchAlgolia', () => {
  let initIndex
  let search

  beforeEach(() => {
    initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })
    search = jest.fn()
    initIndex.mockReturnValue({ search })
  })

  it('should fetch with provided keywords and default page number', () => {
    // given
    const initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })
    const search = jest.fn()
    initIndex.mockReturnValue({ search })
    const keywords = 'searched keywords'

    // when
    fetchAlgolia({
      keywords: keywords,
    })

    // then
    expect(search).toHaveBeenCalledWith(keywords, {
      page: 0,
    })
  })

  describe('keywords', () => {
    it('should fetch with provided keywords', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        geolocation: null,
        keywords: keywords,
      })

      // then
      expect(algoliasearch).toHaveBeenCalledWith(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_API_KEY)
      expect(initIndex).toHaveBeenCalledWith(ALGOLIA_INDEX_NAME)
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch without query parameter when no keyword is provided', () => {
      // when
      fetchAlgolia({
        keywords: '',
        page: 0,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        page: 0,
      })
    })
  })

  describe('geolocation', () => {
    it('should fetch with geolocation coordinates when latitude and longitude are provided', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        geolocation,
        keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
        page: 0,
      })
    })

    it('should not fetch with geolocation coordinates when latitude and longitude are not valid', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: null,
        longitude: null,
      }

      // when
      fetchAlgolia({
        geolocation: geolocation,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch offers with geolocation coordinates, when latitude, longitude are provided and search is not around me', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        geolocation: geolocation,
        keywords: keywords,
        searchAround: false,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
        page: 0,
      })
    })

    it('should fetch offers with geolocation coordinates, when latitude, longitude and radius are provided and search is around me', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        aroundRadius: 15,
        geolocation: geolocation,
        keywords: keywords,
        searchAround: true,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 15000,
        page: 0,
      })
    })

    it('should fetch offers with geolocation coordinates, when latitude, longitude, search is around me, and radius equals zero', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        aroundRadius: 0,
        geolocation: geolocation,
        keywords: keywords,
        searchAround: true,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 1,
        page: 0,
      })
    })

    it('should fetch offers with geolocation coordinates, when latitude, longitude, search is around me, and radius is null', () => {
      // given
      const keywords = 'searched keywords'
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        aroundRadius: null,
        geolocation: geolocation,
        keywords: keywords,
        searchAround: true,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
        page: 0,
      })
    })
  })

  describe('categories', () => {
    it('should fetch with no facetFilters parameter when no category is provided', () => {
      // given
      const keywords = 'searched keywords'
      const offerCategories = []

      // when
      fetchAlgolia({
        keywords: keywords,
        offerCategories: offerCategories,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with facetFilters parameter when one category is provided', () => {
      // given
      const keywords = 'searched keywords'
      const offerCategories = ['LECON']

      // when
      fetchAlgolia({
        keywords: keywords,
        offerCategories: offerCategories,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.searchGroupName:LECON']],
        page: 0,
      })
    })

    it('should fetch with facetFilters parameter when multiple categories are provided', () => {
      // given
      const keywords = 'searched keywords'
      const offerCategories = ['SPECTACLE', 'LIVRE']

      // when
      fetchAlgolia({
        keywords: keywords,
        offerCategories: offerCategories,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.searchGroupName:SPECTACLE', 'offer.searchGroupName:LIVRE']],
        page: 0,
      })
    })
  })

  describe('offer types', () => {
    it('should fetch with no facetFilters when no offer type is provided', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is digital', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: false,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDigital:true'],
        page: 0,
      })
    })

    it('should fetch with no facetFilters when offer is not digital', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false,
        isEvent: false,
        isThing: false,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is physical only', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false,
        isEvent: false,
        isThing: true,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDigital:false', 'offer.isThing:true'],
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is event only', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isEvent:true'],
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is digital and physical', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: true,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isThing:true'],
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is digital or an event', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true,
        isEvent: true,
        isThing: false,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.isDigital:true', 'offer.isEvent:true']],
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer is physical or an event', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: true,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDigital:false'],
        page: 0,
      })
    })

    it('should fetch with no facetFilters when offer is digital, event and thing', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true,
        isEvent: true,
        isThing: true,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with no facetFilters when offer is not digital, not event and not thing', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false,
        isEvent: false,
        isThing: false,
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })
  })

  describe('offer duo', () => {
    it('should fetch with no facetFilters when offer duo is false', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords,
        offerIsDuo: false,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with facetFilters when offer duo is true', () => {
      // given
      const keywords = 'searched keywords'
      const offerIsDuo = true

      // when
      fetchAlgolia({
        keywords: keywords,
        offerIsDuo: offerIsDuo,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDuo:true'],
        page: 0,
      })
    })
  })

  describe('offer is new', () => {
    it('should fetch with no numericFilters when offerIsNew is false', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords,
        offerIsNew: false,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with numericFilters when offerIsNew is true', () => {
      // given
      TIMESTAMP.getFromDate.mockReturnValueOnce(1588762412).mockReturnValueOnce(1589453612)
      const keywords = 'searched keywords'
      const offerIsNew = true

      // when
      fetchAlgolia({
        keywords: keywords,
        offerIsNew: offerIsNew,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: ['offer.stocksDateCreated: 1588762412 TO 1589453612'],
        page: 0,
      })
    })
  })

  describe('offer price', () => {
    it('should fetch with no numericFilters when no price range is specified and offer is not free', () => {
      // given
      const keywords = 'searched keywords'
      const priceRange = []
      const isFree = false

      // when
      fetchAlgolia({
        keywords: keywords,
        isFree,
        priceRange,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
      })
    })

    it('should fetch with numericFilters when offer is free even when priceRange is provided', () => {
      // given
      const keywords = 'searched keywords'
      const offerIsFree = true
      const priceRange = [0, 500]

      // when
      fetchAlgolia({
        keywords,
        offerIsFree,
        priceRange,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: ['offer.prices = 0'],
        page: 0,
      })
    })

    it('should fetch with numericFilters range when price range is provided and offer is not free', () => {
      // given
      const keywords = 'searched keywords'
      const offerIsFree = false
      const priceRange = [0, 50]

      // when
      fetchAlgolia({
        keywords,
        offerIsFree,
        priceRange,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: ['offer.prices: 0 TO 50'],
        page: 0,
      })
    })
  })

  describe('date', () => {
    describe('by date only', () => {
      it('should fetch with date filter when date and today option are provided', () => {
        // Given
        const keywords = 'search keywords'
        const selectedDate = new Date(2020, 3, 19, 11)
        TIMESTAMP.getFromDate.mockReturnValue(123456789)
        TIMESTAMP.getLastOfDate.mockReturnValue(987654321)

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'today',
            selectedDate,
          },
        })

        // Then
        expect(TIMESTAMP.getFromDate).toHaveBeenCalledWith(selectedDate)
        expect(TIMESTAMP.getLastOfDate).toHaveBeenCalledWith(selectedDate)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123456789 TO 987654321`],
          page: 0,
        })
      })

      it('should fetch with date filter when date and currentWeek option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        TIMESTAMP.getFromDate.mockReturnValue(123456789)
        TIMESTAMP.WEEK.getLastFromDate.mockReturnValue(987654321)

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'currentWeek',
            selectedDate,
          },
        })

        // Then
        expect(TIMESTAMP.getFromDate).toHaveBeenCalledWith(selectedDate)
        expect(TIMESTAMP.WEEK.getLastFromDate).toHaveBeenCalledWith(selectedDate)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123456789 TO 987654321`],
          page: 0,
        })
      })

      it('should fetch with date filter when date and currentWeekEnd option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        TIMESTAMP.WEEK_END.getFirstFromDate.mockReturnValue(123456789)
        TIMESTAMP.WEEK.getLastFromDate.mockReturnValue(987654321)

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'currentWeekEnd',
            selectedDate,
          },
        })

        // Then
        expect(TIMESTAMP.WEEK_END.getFirstFromDate).toHaveBeenCalledWith(selectedDate)
        expect(TIMESTAMP.WEEK.getLastFromDate).toHaveBeenCalledWith(selectedDate)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123456789 TO 987654321`],
          page: 0,
        })
      })

      it('should fetch with date filter when date and picked option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        TIMESTAMP.getFirstOfDate.mockReturnValue(123456789)
        TIMESTAMP.getLastOfDate.mockReturnValue(987654321)

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'picked',
            selectedDate,
          },
        })

        // Then
        expect(TIMESTAMP.getFirstOfDate).toHaveBeenCalledWith(selectedDate)
        expect(TIMESTAMP.getLastOfDate).toHaveBeenCalledWith(selectedDate)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123456789 TO 987654321`],
          page: 0,
        })
      })
    })

    describe('by time only', () => {
      it('should fetch with time filter when timeRange is provided', () => {
        // Given
        const timeRange = [18, 22]
        computeTimeRangeFromHoursToSeconds.mockReturnValue([64800, 79200])

        // When
        fetchAlgolia({ timeRange })

        // Then
        expect(computeTimeRangeFromHoursToSeconds).toHaveBeenCalledWith(timeRange)
        expect(search).toHaveBeenCalledWith('', {
          numericFilters: [`offer.times: 64800 TO 79200`],
          page: 0,
        })
      })
    })

    describe('by date and time', () => {
      it('should fetch with date filter when timeRange, date and today option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        const timeRange = [18, 22]
        TIMESTAMP.getAllFromTimeRangeAndDate.mockReturnValue([123, 124])

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'today',
            selectedDate,
          },
          timeRange: timeRange,
        })

        // Then
        expect(TIMESTAMP.getAllFromTimeRangeAndDate).toHaveBeenCalledWith(selectedDate, timeRange)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123 TO 124`],
          page: 0,
        })
      })

      it('should fetch with date filter when timeRange, date and currentWeek option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        const timeRange = [18, 22]
        TIMESTAMP.WEEK.getAllFromTimeRangeAndDate.mockReturnValue([
          [123, 124],
          [225, 226],
          [327, 328],
        ])

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'currentWeek',
            selectedDate,
          },
          timeRange: timeRange,
        })

        // Then
        expect(TIMESTAMP.WEEK.getAllFromTimeRangeAndDate).toHaveBeenCalledWith(
          selectedDate,
          timeRange
        )
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [
            [`offer.dates: 123 TO 124`, `offer.dates: 225 TO 226`, `offer.dates: 327 TO 328`],
          ],
          page: 0,
        })
      })

      it('should fetch with date filter when timeRange, date and currentWeekEnd option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        const timeRange = [18, 22]
        TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate.mockReturnValue([
          [123, 124],
          [225, 226],
        ])

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'currentWeekEnd',
            selectedDate,
          },
          timeRange: timeRange,
        })

        // Then
        expect(TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate).toHaveBeenCalledWith(
          selectedDate,
          timeRange
        )
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [[`offer.dates: 123 TO 124`, `offer.dates: 225 TO 226`]],
          page: 0,
        })
      })

      it('should fetch with date filter when timeRange, date and picked option are provided', () => {
        // Given
        const keywords = ''
        const selectedDate = new Date(2020, 3, 19, 11)
        const timeRange = [18, 22]
        TIMESTAMP.getAllFromTimeRangeAndDate.mockReturnValue([123, 124])

        // When
        fetchAlgolia({
          keywords,
          date: {
            option: 'picked',
            selectedDate,
          },
          timeRange: timeRange,
        })

        // Then
        expect(TIMESTAMP.getAllFromTimeRangeAndDate).toHaveBeenCalledWith(selectedDate, timeRange)
        expect(search).toHaveBeenCalledWith(keywords, {
          numericFilters: [`offer.dates: 123 TO 124`],
          page: 0,
        })
      })
    })
  })

  describe('multiple parameters', () => {
    it('should fetch with price and date numericFilters', () => {
      // Given
      TIMESTAMP.getFirstOfDate.mockReturnValue(123456789)
      TIMESTAMP.getLastOfDate.mockReturnValue(987654321)
      const keywords = ''
      const isFree = true
      const selectedDate = new Date(2020, 3, 19, 11)

      // When
      fetchAlgolia({
        date: {
          option: 'picked',
          selectedDate,
        },
        offerIsFree: isFree,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: ['offer.prices = 0', 'offer.dates: 123456789 TO 987654321'],
        page: 0,
      })
    })

    it('should fetch with price and time numericFilters', () => {
      // Given
      computeTimeRangeFromHoursToSeconds.mockReturnValue([123456789, 987654321])
      const keywords = ''
      const isFree = true
      const timeRange = [10, 17]

      // When
      fetchAlgolia({
        timeRange,
        offerIsFree: isFree,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: ['offer.prices = 0', 'offer.times: 123456789 TO 987654321'],
        page: 0,
      })
    })

    it('should fetch with price, date and time numericFilters', () => {
      // Given
      TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate.mockReturnValue([
        [123456789, 987654321],
        [123, 1234],
      ])
      const keywords = ''
      const isFree = true
      const selectedDate = new Date(2020, 3, 19, 11)

      // When
      fetchAlgolia({
        date: {
          option: 'currentWeekEnd',
          selectedDate,
        },
        timeRange: [18, 22],
        offerIsFree: isFree,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: [
          'offer.prices = 0',
          ['offer.dates: 123456789 TO 987654321', 'offer.dates: 123 TO 1234'],
        ],
        page: 0,
      })
    })

    it('should fetch with all given search parameters', () => {
      // given
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const keywords = 'searched keywords'
      const offerCategories = ['LECON', 'VISITE']
      const offerTypes = {
        isDigital: true,
        isEvent: false,
        isThing: false,
      }
      const page = 2

      // when
      fetchAlgolia({
        geolocation: geolocation,
        keywords: keywords,
        offerCategories: offerCategories,
        offerTypes: offerTypes,
        page: page,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: page,
        facetFilters: [
          ['offer.searchGroupName:LECON', 'offer.searchGroupName:VISITE'],
          'offer.isDigital:true',
        ],
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })

    it('should fetch event offers for categories pratique & spectacle around me', () => {
      // given
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const keywords = ''
      const offerCategories = ['PRATIQUE', 'SPECTACLE']
      const offerIsDuo = false
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      // when
      fetchAlgolia({
        geolocation,
        keywords,
        offerCategories,
        offerIsDuo,
        offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
        facetFilters: [
          ['offer.searchGroupName:PRATIQUE', 'offer.searchGroupName:SPECTACLE'],
          'offer.isEvent:true',
        ],
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })

    it('should fetch duo & free event offers for categories pratique & spectacle around me', () => {
      // given
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const keywords = ''
      const offerCategories = ['PRATIQUE', 'SPECTACLE']
      const offerIsDuo = true
      const priceRange = [5, 40]
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false,
      }

      // when
      fetchAlgolia({
        geolocation,
        keywords,
        offerCategories,
        offerIsDuo,
        priceRange,
        offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
        facetFilters: [
          ['offer.searchGroupName:PRATIQUE', 'offer.searchGroupName:SPECTACLE'],
          'offer.isEvent:true',
          'offer.isDuo:true',
        ],
        numericFilters: ['offer.prices: 5 TO 40'],
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })
  })

  describe('tags', () => {
    it('should fetch with no facetFilters parameter when no tags are provided', () => {
      // given
      const tags = []

      // when
      fetchAlgolia({
        tags: tags,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        page: 0,
      })
    })

    it('should fetch with facetFilters parameter when tags are provided', () => {
      // given
      const tags = ['Semaine du 14 juillet', 'Offre cinema spéciale pass culture']

      // when
      fetchAlgolia({
        tags: tags,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        page: 0,
        facetFilters: [
          ['offer.tags:Semaine du 14 juillet', 'offer.tags:Offre cinema spéciale pass culture'],
        ],
      })
    })
  })

  describe('hitsPerPage', () => {
    it('should fetch with no hitsPerPage parameter when not provided', () => {
      // given
      const hitsPerPage = null

      // when
      fetchAlgolia({
        hitsPerPage,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        page: 0,
      })
    })

    it('should fetch with hitsPerPage when provided', () => {
      // given
      const hitsPerPage = 5

      // when
      fetchAlgolia({
        hitsPerPage,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        hitsPerPage,
        page: 0,
      })
    })
  })

  describe('beginningDatetime & endingDatetime', () => {
    it('should fetch from the beginning datetime', () => {
      // Given
      const beginningDatetime = new Date(2020, 8, 1)
      const keywords = ''
      TIMESTAMP.getFromDate.mockReturnValueOnce(1596240000)

      // When
      fetchAlgolia({
        keywords,
        beginningDatetime,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: [`offer.dates >= 1596240000`],
        page: 0,
      })
    })

    it('should fetch until the ending datetime', () => {
      // Given
      const endingDatetime = new Date(2020, 8, 1)
      const keywords = ''
      TIMESTAMP.getFromDate.mockReturnValueOnce(1596240000)

      // When
      fetchAlgolia({
        keywords,
        endingDatetime,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: [`offer.dates <= 1596240000`],
        page: 0,
      })
    })

    it('should fetch from the beginning datetime to the ending datetime', () => {
      // Given
      const beginningDatetime = new Date(2020, 8, 1)
      const endingDatetime = new Date(2020, 8, 2)

      const keywords = ''
      TIMESTAMP.getFromDate.mockReturnValueOnce(1596240000).mockReturnValueOnce(1596326400)

      // When
      fetchAlgolia({
        keywords,
        beginningDatetime,
        endingDatetime,
      })

      // Then
      expect(search).toHaveBeenCalledWith(keywords, {
        numericFilters: [`offer.dates: 1596240000 TO 1596326400`],
        page: 0,
      })
    })
  })
})
