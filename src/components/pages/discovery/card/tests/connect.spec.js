import moment from 'moment'

import { mapDispatchToProps, mapStateToProps } from '../connect'
import { configureStore } from '../../../../../utils/store'

navigator.geolocation = {}

describe('src | components | pages | discovery | card | connect', () => {
  describe('mapStateToProps', () => {
    it('default return', () => {
      // given
      const { store } = configureStore()
      const state = store.getState()
      const ownProps = {
        match: { params: {} },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      const expected = {
        areDetailsVisible: false,
        recommendation: undefined,
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    it('handleReadRecommendation', () => {
      // given
      const { store } = configureStore()
      const recommendation = { id: 'AE' }

      // when
      mapDispatchToProps(store.dispatch).handleReadRecommendation(
        recommendation
      )

      // then
      const {
        data: { readRecommendations },
      } = store.getState()
      expect(readRecommendations.length).toStrictEqual(1)
      expect(readRecommendations[0].id).toStrictEqual('AE')
      expect(
        moment(readRecommendations[0].dateRead).isSame(moment.utc(), 'minutes')
      ).toStrictEqual(true)
    })
  })
})
