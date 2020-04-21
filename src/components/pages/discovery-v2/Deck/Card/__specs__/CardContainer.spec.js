import moment from 'moment'

import { mapDispatchToProps, mapStateToProps } from '../CardContainer'
import { configureStore } from '../../../../../../utils/store'

navigator.geolocation = {}

jest.mock('redux-thunk-data', () => ({
  ...jest.requireActual('redux-thunk-data'),
  requestData: () => {
    return {
      type: 'REQUEST_DATA',
      config: {
        apiPath: '/seen_offers',
        body: {
          offerId: 'AE',
          userId: 'FY',
        },
        method: 'PUT',
      },
    }
  },
}))

describe('src | components | pages | discovery | Deck | Card | CardContainer', () => {
  describe('mapStateToProps', () => {
    it('default return', () => {
      // given
      const { store } = configureStore()
      const state = store.getState()

      state.data.users = [
        {
          id: 'FY',
        },
      ]
      const ownProps = {
        match: {
          params: {
            offerId: 'AE',
          },
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        recommendation: undefined,
        seenOffer: {
          offerId: 'AE',
          userId: 'FY',
        },
      })
    })
  })

  describe('mapDispatchToProps', () => {
    it('handleReadRecommendation', () => {
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
      expect(moment(readRecommendations[0].dateRead).isSame(moment.utc(), 'minutes')).toStrictEqual(
        true
      )
    })

    it('handleSeenOffer', () => {
      // given
      const dispatch = jest.fn()
      const seenOffer = {
        offerId: 'AE',
        userId: 'FY',
      }

      // when
      mapDispatchToProps(dispatch).handleSeenOffer(seenOffer)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        type: 'REQUEST_DATA',
        config: {
          apiPath: '/seen_offers',
          body: seenOffer,
          method: 'PUT',
        },
      })
    })
  })
})
