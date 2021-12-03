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
    }

    // when
    const result = mapStateToProps(state, props)

    // then
    expect(result).toStrictEqual({
      geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
      redirectToSearchMainPage: expect.any(Function),
    })
  })

  it('should redirect to search main page', () => {
    // given
    const push = jest.fn()
    const props = { history: { push } }
    const state = {}

    // when
    mapStateToProps(state, props).redirectToSearchMainPage()

    // then
    expect(push).toHaveBeenCalledWith('/recherche')
  })
})
