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
  it('should call Algolia with provided keywords and page number', () => {
    // given
    const initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })
    const search = jest.fn()
    initIndex.mockReturnValue({ search })
    const searchedKeywords = 'searched keywords'
    const pageRequested = 0

    // when
    fetchAlgolia({
      geolocationCoordinates: null,
      keywords: searchedKeywords,
      page: pageRequested,
    })

    // then
    expect(algoliasearch).toHaveBeenCalledWith(
      WEBAPP_ALGOLIA_APPLICATION_ID,
      WEBAPP_ALGOLIA_SEARCH_API_KEY
    )
    expect(initIndex).toHaveBeenCalledWith(WEBAPP_ALGOLIA_INDEX_NAME)
    expect(search).toHaveBeenCalledWith(searchedKeywords, {
      page: pageRequested
    })
  })

  it('should call Algolia without query parameter when no keyword is provided', () => {
    // given
    const initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })
    const search = jest.fn()
    initIndex.mockReturnValue({ search })

    // when
    fetchAlgolia({
      geolocationCoordinates: null,
      keywords: '',
      page: 0,
    })

    // then
    expect(search).toHaveBeenCalledWith('', {
      page: 0
    })
  })

  describe('geolocation parameters', () => {
    it('should call Algolia with geolocation coordinates when latitude and longitude are provided', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }

      // when
      fetchAlgolia({
        geolocationCoordinates: geolocation,
        keywords: searchedKeywords,
        page: 0
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested,
        aroundLatLng: '42, 43',
        aroundRadius: 'all'
      })
    })

    it('should not call Algolia with geolocation coordinates when latitude and longitude are not valid', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = {
        latitude: null,
        longitude: null,
      }

      // when
      fetchAlgolia({
        geolocationCoordinates: geolocation,
        keywords: searchedKeywords,
        page: 0
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested
      })
    })
  })

  describe('categories filter parameter', () => {
    it('should call Algolia with filter parameter if one category is provided', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = null
      const categoriesFilter = ['Pratique artistique']

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested,
        filters: 'offer.label:"Pratique artistique"'
      })
    })

    it('should call Algolia with formatted filter parameter if multiple categories are provided', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = null
      const categoriesFilter = ['Spectacle', 'Abonnement spectacles']

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested,
        filters: 'offer.label:"Spectacle" OR offer.label:"Abonnement spectacles"'
      })
    })

    it('should call Algolia with no filter if one category is an empty string', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = null
      const categoriesFilter = ['']

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested,
      })
    })
  })

  describe('sorting parameter', () => {
    it('should call Algolia using right index if index suffix is provided', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = null
      const categoriesFilter = []
      const indexSuffix = '_by_proximity'

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_proximity')
    })

    it('should call Algolia using default index if no index suffix is provided', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 0
      const geolocation = null
      const categoriesFilter = []
      const indexSuffix = ''

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested
      })
      expect(initIndex).toHaveBeenCalledWith('indexName')
    })
  })

  describe('multiple parameters', () => {
    it('should call Algolia with all given search parameters', () => {
      // given
      const initIndex = jest.fn()
      algoliasearch.mockReturnValue({ initIndex })
      const search = jest.fn()
      initIndex.mockReturnValue({ search })
      const searchedKeywords = 'searched keywords'
      const pageRequested = 2
      const geolocation = {
        latitude: 42,
        longitude: 43,
      }
      const categoriesFilter = ['Pratique artistique']
      const indexSuffix = '_by_price'

      // when
      fetchAlgolia({
        categories: categoriesFilter,
        geolocationCoordinates: geolocation,
        indexSuffix: indexSuffix,
        keywords: searchedKeywords,
        page: pageRequested
      })

      // then
      expect(search).toHaveBeenCalledWith(searchedKeywords, {
        page: pageRequested,
        filters: 'offer.label:"Pratique artistique"',
        aroundLatLng: '42, 43',
        aroundRadius: 'all'
      })
      expect(initIndex).toHaveBeenCalledWith('indexName_by_price')
    })
  })
})
