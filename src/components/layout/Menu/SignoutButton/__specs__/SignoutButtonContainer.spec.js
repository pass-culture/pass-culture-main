import { createBrowserHistory } from 'history'

import { mapDispatchToProps } from '../SignoutButtonContainer'
import { configureStore } from '../../../../../utils/store'

jest.mock('redux-thunk-data', () => ({
  ...jest.requireActual('redux-thunk-data'),
  requestData: config => {
    config.handleSuccess()
    return { type: 'REQUEST_DATA' }
  },
}))

describe('src | components | layout | Menu | SignoutButton | SignoutButtonContainer', () => {
  describe('mapDispatchToProps()', () => {
    describe('onSignOutClick()', () => {
      it('should land to /connexion, close the menu, reset readRecommendations and pagination in store', () => {
        // given
        const initialPagination = {
          page: 4,
          seed: 0.1,
          seedLastRequestTimestamp: 11111111112,
        }
        const { store } = configureStore({
          data: {
            bookings: [{ id: 'b1' }],
            features: [{ id: 'f1' }],
            users: [{ id: 'u1' }],
          },
          menu: true,
          pagination: initialPagination
        })
        const history = createBrowserHistory()
        const readRecommendations = [
          { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AE' },
          { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AF' },
        ]

        // when
        mapDispatchToProps(store.dispatch).onSignOutClick({
          history,
          readRecommendations,
        })()

        // then
        const { data, menu, pagination } = store.getState()
        expect(menu).toBe(false)
        expect(data).toStrictEqual({
          _persist: {
            rehydrated: false,
            version: -1,
          },
          bookings: [],
          favorites: [],
          features: [{ id: 'f1' }],
          mediations: [],
          musicTypes: [],
          offers: [],
          readRecommendations: [],
          recommendations: [],
          showTypes: [],
          stocks: [],
          types: [],
          users: [],
        })
        expect(data.readRecommendations).toHaveLength(0)
        expect(history.location.pathname).toBe('/connexion')
        expect(pagination.page).toBe(1)
        expect(pagination.seed).not.toStrictEqual(initialPagination.seed)
        expect(pagination.seedLastRequestTimestamp).not.toStrictEqual(initialPagination.seedLastRequestTimestamp)
      })
    })
  })
})
