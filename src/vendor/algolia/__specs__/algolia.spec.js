import algoliasearch from 'algoliasearch'
import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../../utils/config'
import { fetchAlgolia } from '../algolia'

jest.mock('algoliasearch')
jest.mock('../../../utils/config', () => ({
  WEBAPP_ALGOLIA_APPLICATION_ID: 'appId',
  WEBAPP_ALGOLIA_INDEX_NAME: 'indexName',
  WEBAPP_ALGOLIA_SEARCH_API_KEY: 'apiKey',
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
      facetFilters: [],
      page: 0
    })
  })

  describe('keywords', () => {
    it('should fetch with provided keywords', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        geolocationCoordinates: null,
        keywords: keywords,
      })

      // then
      expect(algoliasearch).toHaveBeenCalledWith(
        WEBAPP_ALGOLIA_APPLICATION_ID,
        WEBAPP_ALGOLIA_SEARCH_API_KEY
      )
      expect(initIndex).toHaveBeenCalledWith(WEBAPP_ALGOLIA_INDEX_NAME)
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
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
        facetFilters: [],
        page: 0
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
        geolocationCoordinates: geolocation,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
        facetFilters: [],
        page: 0
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
        geolocationCoordinates: geolocation,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
    })
  })

  describe('categories', () => {
    it('should fetch with no facetFilters parameter when no category is provided', () => {
      // given
      const keywords = 'searched keywords'
      const categories = []

      // when
      fetchAlgolia({
        categories: categories,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
    })

    it('should fetch with facetFilters parameter when one category is provided', () => {
      // given
      const keywords = 'searched keywords'
      const categories = ['LECON']

      // when
      fetchAlgolia({
        categories: categories,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.category:LECON']],
        page: 0,
      })
    })

    it('should fetch with facetFilters parameter when multiple categories are provided', () => {
      // given
      const keywords = 'searched keywords'
      const categories = ['SPECTACLE', 'LIVRE']

      // when
      fetchAlgolia({
        categories: categories,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.category:SPECTACLE', 'offer.category:LIVRE']],
        page: 0,
      })
    })
  })

  describe('sorting', () => {
    it('should fetch with given index when index suffix is provided', () => {
      // given
      const keywords = 'searched keywords'
      const indexSuffix = '_by_proximity'

      // when
      fetchAlgolia({
        indexSuffix: indexSuffix,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_proximity')
    })

    it('should fetch using default index when no index suffix is provided', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })
  })

  describe('offer types', () => {
    it('should fetch with empty facetFilters when no offer type is provided', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
    })

    it('should fetch with facetFilters when offer is digital', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true,
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

    it('should fetch with empty facetFilters when offer is not digital', () => {
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDigital:false', 'offer.isThing:true'],
        page: 0
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isEvent:true'],
        page: 0
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isThing:true'],
        page: 0
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [['offer.isDigital:true', 'offer.isEvent:true']],
        page: 0
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ['offer.isDigital:false'],
        page: 0
      })
    })

    it('should fetch with empty facetFilters when offer is digital, event and thing', () => {
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
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [],
        page: 0
      })
    })

    it('should fetch with empty facetFilters when offer is not digital, not event and not thing', () => {
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
        facetFilters: [],
        page: 0,
      })
    })
  })

  describe('multiple parameters', () => {
    it('should fetch with all given search parameters', () => {
      // given
      const keywords = 'searched keywords'
      const page = 2
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const categories = ['LECON', 'VISITE']
      const indexSuffix = '_by_price'
      const offerTypes = {
        isDigital: true,
      }

      // when
      fetchAlgolia({
        categories: categories,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: keywords,
        offerTypes: offerTypes,
        page: page,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: page,
        facetFilters: [['offer.category:LECON', 'offer.category:VISITE'], 'offer.isDigital:true'],
        aroundLatLng: '42, 43',
        aroundRadius: 'all',
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_price')
    })

    it('should fetch event offers for category spectacle around me ordered by price', () => {
      // given
      const keywords = ''
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const categories = ['PRATIQUE', 'SPECTACLE']
      const indexSuffix = '_by_price'
      const offerTypes = {
        isDigital: false,
        isEvent: true,
        isThing: false
      }

      // when
      fetchAlgolia({
        categories: categories,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: keywords,
        offerTypes: offerTypes,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0,
        facetFilters: [["offer.category:PRATIQUE", "offer.category:SPECTACLE"], "offer.isEvent:true"],
        aroundLatLng: '42, 43',
        aroundRadius: 'all'
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_price')
    })
  })
})
