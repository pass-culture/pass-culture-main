import algoliasearch from 'algoliasearch'
import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../../../../utils/config'
import { fetchAlgolia } from '../algoliaService'

jest.mock('algoliasearch')
jest.mock('../../../../../utils/config', () => ({
  WEBAPP_ALGOLIA_APPLICATION_ID: 'appId',
  WEBAPP_ALGOLIA_INDEX_NAME: 'indexName',
  WEBAPP_ALGOLIA_SEARCH_API_KEY: 'apiKey',
}))

describe('fetchAlgolia', () => {
  it('should not call Algolia when no keyword is provided', () => {
    // Given
    const initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })

    // When
    fetchAlgolia('', 0, null)

    // Then
    expect(algoliasearch).not.toHaveBeenCalled()
    expect(initIndex).not.toHaveBeenCalled()
  })

  it('should call Algolia with provided keywords and page number', () => {
    // Given
    const initIndex = jest.fn()
    algoliasearch.mockReturnValue({ initIndex })
    const search = jest.fn()
    initIndex.mockReturnValue({ search })
    const searchedKeywords = 'searched keywords'
    const pageRequested = 0

    // When
    fetchAlgolia(searchedKeywords, pageRequested, null)

    // Then
    expect(algoliasearch).toHaveBeenCalledWith(
      WEBAPP_ALGOLIA_APPLICATION_ID,
      WEBAPP_ALGOLIA_SEARCH_API_KEY
    )
    expect(initIndex).toHaveBeenCalledWith(WEBAPP_ALGOLIA_INDEX_NAME)
    expect(search).toHaveBeenCalledWith({
      query: searchedKeywords,
      page: pageRequested,
    })
  })

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
    fetchAlgolia(searchedKeywords, 0, geolocation)

    // then
    expect(search).toHaveBeenCalledWith({
      query: searchedKeywords,
      page: pageRequested,
      aroundLatLng: '42, 43',
      aroundRadius: 'all',
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
    fetchAlgolia(searchedKeywords, 0, geolocation)

    // then
    expect(search).toHaveBeenCalledWith({
      query: searchedKeywords,
      page: pageRequested,
    })
  })
})
