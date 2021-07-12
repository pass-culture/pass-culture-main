import { mapStateToProps } from '../SearchContainer'

jest.mock('../../../../utils/geolocation', () => ({
  isGeolocationEnabled: jest.fn().mockReturnValue(true),
  isUserAllowedToSelectCriterion: jest.fn(),
}))

describe('mapStateToProps', () => {
  it('should return an object with geolocation and redirect function', () => {
    // given
    const push = jest.fn()
    const props = { history: { push } }
    const state = {
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
      data: { features: [{ isActive: true, nameKey: 'USE_APP_SEARCH_ON_WEBAPP' }] },
    }

    // when
    const result = mapStateToProps(state, props)

    // then
    expect(result).toStrictEqual({
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
      redirectToSearchMainPage: expect.any(Function),
      useAppSearch: true,
    })
  })

  it('should redirect to search main page', () => {
    // given
    const push = jest.fn()
    const props = { history: { push } }
    const state = {
      data: { features: [{ isActive: true, nameKey: 'USE_APP_SEARCH_ON_WEBAPP' }] },
    }

    // when
    mapStateToProps(state, props).redirectToSearchMainPage()

    // then
    expect(push).toHaveBeenCalledWith('/recherche')
  })

  it('should return useAppSearch=False if the feature is disabled', () => {
    // Given
    const state = {
      data: { features: [{ isActive: false, nameKey: 'USE_APP_SEARCH_ON_WEBAPP' }] },
    }

    // When
    const props = mapStateToProps(state)

    // Then
    expect(props.useAppSearch).toBe(false)
  })

  it('should return useAppSearch=True if the feature is enabled', () => {
    // Given
    const state = {
      data: { features: [{ isActive: true, nameKey: 'USE_APP_SEARCH_ON_WEBAPP' }] },
    }

    // When
    const props = mapStateToProps(state)

    // Then
    expect(props.useAppSearch).toBe(true)
  })
})
