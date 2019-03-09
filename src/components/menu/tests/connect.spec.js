import { createBrowserHistory } from 'history'

import { mapDispatchToProps, mapStateToProps } from '../connect'
import { configureStore } from '../../../utils/store'

jest.mock('redux-saga-data', () => ({
  ...jest.requireActual('redux-saga-data'),
  requestData: config => {
    config.handleSuccess()
    return { type: 'REQUEST_DATA' }
  },
}))

describe('src | components | menu | connect', () => {
  describe('mapStateToProps', () => {
    it('default return', () => {
      // given
      const { store } = configureStore()
      const state = store.getState()

      // when
      const result = mapStateToProps(state)

      // then
      const expected = {
        readRecommendations: [],
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    it('onSignoutClick', () => {
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
      expect(menu).toStrictEqual(false)
      expect(data.readRecommendations.length).toStrictEqual(0)
      expect(history.location.pathname).toStrictEqual('/connexion')
    })
  })
})
