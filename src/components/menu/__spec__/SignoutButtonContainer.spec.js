import { createBrowserHistory } from 'history'
import { requestData } from 'redux-saga-data'

import { mapDispatchToProps } from '../SignoutButtonContainer'
import { configureStore } from '../../../utils/store'

jest.mock('redux-saga-data', () => ({
  ...jest.requireActual('redux-saga-data'),
  requestData: config => {
    config.handleSuccess()
    return { type: 'REQUEST_DATA' }
  },
}))

// jest.mock('redux-saga-data', () => ({
//   requestData: jest.fn(),
// }))

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

      it.skip('should called handleRequestSignout()', () => {
        // given
        const { store } = configureStore({ menu: true })
        const history = createBrowserHistory()
        const readRecommendations = []
        // const handleRequestSignout = jest.fn()

        // when
        mapDispatchToProps(store.dispatch).onSignoutClick({
          history,
          readRecommendations,
        })()
        // console.log(history)

        // then
        expect(requestData).toHaveBeenCalledWith({})
      })
    })
  })
})
