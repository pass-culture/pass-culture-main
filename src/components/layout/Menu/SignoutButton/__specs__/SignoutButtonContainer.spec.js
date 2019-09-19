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
    describe('onSignoutClick()', () => {
      it('should land to /connexion, close the menu and reset readRecommendations in store', () => {
        // given
        const { store } = configureStore({
          data: {
            bookings: [{ id: 'b1' }],
            features: [{ id: 'f1' }],
            users: [{ id: 'u1' }],
          },
          menu: true,
        })
        const history = createBrowserHistory()
        const readRecommendations = [
          { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AE' },
          { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AF' },
        ]

        // when
        mapDispatchToProps(store.dispatch).onSignoutClick({
          history,
          readRecommendations,
        })()

        // then
        const { data, menu } = store.getState()
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
      })
    })
  })
})
