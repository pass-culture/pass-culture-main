import { createBrowserHistory } from 'history'

import { mapDispatchToProps } from '../SignoutButtonContainer'
import { configureStore } from '../../../../../utils/store'

jest.mock('redux-saga-data', () => ({
  ...jest.requireActual('redux-saga-data'),
  requestData: config => {
    config.handleSuccess()
    return { type: 'REQUEST_DATA' }
  },
}))

describe('src | components | menu | SignoutButtonContainer', () => {
  describe('mapDispatchToProps()', () => {
    describe('onSignoutClick()', () => {
      it('should dispatch request data', () => {
        // given
        const { store } = configureStore({ menu: true })
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
        expect(data.readRecommendations).toHaveLength(0)
        expect(history.location.pathname).toBe('/connexion')
      })
    })
  })
})
