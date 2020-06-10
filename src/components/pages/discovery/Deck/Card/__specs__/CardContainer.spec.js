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
        },
        method: 'PUT',
      },
    }
  },
}))

describe('src | components | pages | discovery | Deck | Card | CardContainer', () => {
  describe('mapStateToProps', () => {
    describe('when there are no recommendations in the store', () => {
      it('should return undefined', () => {
        // given
        const { store } = configureStore()
        const state = store.getState()

        state.data = {
          features: [
            {
              id: '2M',
              isActive: true,
              nameKey: 'SAVE_SEEN_OFFERS',
            },
          ],
        }
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
          },
          isSeenOfferFeatureActive: true,
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

      it('handleSeenOffer', () => {
        // given
        const dispatch = jest.fn()
        const seenOffer = {
          offerId: 'AE',
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
})
