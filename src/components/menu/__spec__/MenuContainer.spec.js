import { mapDispatchToProps, mapStateToProps } from '../MenuContainer'
import { configureStore } from '../../../utils/store'

describe('src | components | menu | MenuContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return any current user', () => {
      // given
      const { store } = configureStore()
      const state = store.getState()

      // when
      const result = mapStateToProps(state)

      // then
      expect(result).toStrictEqual({
        currentUser: undefined,
        readRecommendations: [],
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should dispatch toggleOverlay', () => {
      // given
      const dispatch = jest.fn()

      // when
      mapDispatchToProps(dispatch).toggleOverlay()

      // then
      expect(dispatch).toHaveBeenCalledWith({ type: 'TOGGLE_OVERLAY' })
    })
  })
})
