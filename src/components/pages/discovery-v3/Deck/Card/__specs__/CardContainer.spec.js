import moment from 'moment'

import { mapDispatchToProps, mapStateToProps } from '../CardContainer'
import { configureStore } from '../../../../../../utils/store'

navigator.geolocation = {}

describe('src | components | pages | discovery | Deck | Card | CardContainer', () => {
  describe('mapStateToProps', () => {
    describe('when there are no recommendations in the store', () => {
      it('should return undefined', () => {
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
          recommendation: undefined,
        }
        expect(result).toStrictEqual(expected)
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('handleReadRecommendation', () => {
      it('should save the read date of the offer', () => {
        // given
        const { store } = configureStore()
        const recommendation = { id: 'AE' }

        // when
        mapDispatchToProps(store.dispatch).handleReadRecommendation(recommendation)

        // then
        const {
          data: { readRecommendations },
        } = store.getState()
        expect(readRecommendations).toHaveLength(1)
        expect(readRecommendations[0].id).toStrictEqual('AE')
        expect(
          moment(readRecommendations[0].dateRead).isSame(moment.utc(), 'minutes')
        ).toStrictEqual(true)
      })
    })
  })
})
