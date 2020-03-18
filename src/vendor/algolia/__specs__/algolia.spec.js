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

  it('should call Algolia with provided keywords and default page number', () => {
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
      page: 0
    })
  })

  describe('keywords', () => {
    it('should call Algolia with provided keywords', () => {
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
        page: 0
      })
    })

    it('should call Algolia without query parameter when no keyword is provided', () => {
      // when
      fetchAlgolia({
        keywords: '',
        page: 0,
      })

      // then
      expect(search).toHaveBeenCalledWith('', {
        page: 0
      })
    })
  })

  describe('geolocation', () => {
    it('should call Algolia with geolocation coordinates when latitude and longitude are provided', () => {
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
        page: 0
      })
    })

    it('should not call Algolia with geolocation coordinates when latitude and longitude are not valid', () => {
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
        page: 0
      })
    })
  })

  describe('categories', () => {
    it('should call Algolia with no facetFilters parameter when no category is provided', () => {
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
        page: 0
      })
    })

    it('should call Algolia with facetFilters parameter when one category is provided', () => {
      // given
      const keywords = 'searched keywords'
      const categories = ['Pratique artistique']

      // when
      fetchAlgolia({
        categories: categories,
        keywords: keywords
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [["offer.label:Pratique artistique"]],
        page: 0,
      })
    })

    it('should call Algolia with facetFilters parameter when multiple categories are provided', () => {
      // given
      const keywords = 'searched keywords'
      const categories = ['Spectacle', 'Abonnement spectacles']

      // when
      fetchAlgolia({
        categories: categories,
        keywords: keywords,
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: [["offer.label:Spectacle", "offer.label:Abonnement spectacles"]],
        page: 0
      })
    })
  })

  describe('sorting', () => {
    it('should call Algolia with given index when index suffix is provided', () => {
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
        page: 0
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_proximity')
    })

    it('should call Algolia using default index when no index suffix is provided', () => {
      // given
      const keywords = 'searched keywords'

      // when
      fetchAlgolia({
        keywords: keywords
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })
  })

  describe('offer types', () => {
    it('should call Algolia with no facetFilters parameter when no offer type is provided', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = null

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: 0
      })
    })

    it('should call Algolia with facetFilters parameter when offer is digital', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: true
      }

      // when
      fetchAlgolia({
        keywords: keywords,
        offerTypes: offerTypes
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        facetFilters: ["offer.isDigital:true"],
        page: 0
      })
    })

    it('should call Algolia with empty facetFilters parameter when offer is not digital', () => {
      // given
      const keywords = 'searched keywords'
      const offerTypes = {
        isDigital: false
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
  })

  describe('multiple parameters', () => {
    it('should call Algolia with all given search parameters', () => {
      // given
      const keywords = 'searched keywords'
      const page = 2
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const categories = ['Pratique artistique', 'Musée']
      const indexSuffix = '_by_price'
      const offerTypes = {
        isDigital: true
      }

      // when
      fetchAlgolia({
        categories: categories,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: keywords,
        offerTypes: offerTypes,
        page: page
      })

      // then
      expect(search).toHaveBeenCalledWith(keywords, {
        page: page,
        facetFilters: [["offer.label:Pratique artistique", "offer.label:Musée"], "offer.isDigital:true"],
        aroundLatLng: '42, 43',
        aroundRadius: 'all'
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_price')
    })
  })
})
