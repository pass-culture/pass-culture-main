import { mapStateToProps } from '../FiltersContainer'

describe('components | FiltersContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object with the right props', () => {
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
        isGeolocationEnabled: true,
        isUserAllowedToSelectCriterion: expect.any(Function),
        redirectToSearchFiltersPage: expect.any(Function),
      })
    })

    it('should redirect to filters page', () => {
      // given
      const push = jest.fn()
      const props = { history: { location: { search: '?mots-cles=librairie' }, push } }
      const state = {
        geolocation: { latitude: 48.8533261, longitude: 2.3451865 },
      }

      // when
      mapStateToProps(state, props).redirectToSearchFiltersPage()

      // then
      expect(push).toHaveBeenCalledWith('/recherche-offres/resultats/filtres?mots-cles=librairie')
    })
  })
})
