import { mapStateToProps } from '../SearchAlgoliaContainer'

describe('mapStateToProps', () => {
  it('should return an object with geolocation and redirect function', () => {
    // given
    const push = jest.fn()
    const props = { history: { push } }
    const state = {
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
    }

    // when
    const result = mapStateToProps(state, props)

    // then
    expect(result).toStrictEqual({
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
      redirectToSearchMainPage: expect.any(Function),
      isGeolocationEnabled: expect.any(Function),
    })
  })

  it('should redirect to search main page', () => {
    // given
    const push = jest.fn()
    const props = { history: { push } }

    // when
    mapStateToProps({}, props).redirectToSearchMainPage()

    // then
    expect(push).toHaveBeenCalledWith('/recherche-offres')
  })

  it('should return true if user authorized geolocation', () => {
    // Given
    const state = {
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
    }
    // When
    const result = mapStateToProps(state).isGeolocationEnabled()
    // Then
    expect(result).toBe(true)
  })

  it('should return false if user refused geolocation', () => {
    // Given
    const state = {
      geolocation: { latitude:null, longitude: null },
    }
    // When
    const result = mapStateToProps(state).isGeolocationEnabled()
    // Then
    expect(result).toBe(false)
  })
})
