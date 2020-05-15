import { createBrowserHistory } from 'history'

import { mapDispatchToProps } from '../SignoutLinkContainer'
import { configureStore } from '../../../../../utils/store'

jest.mock('redux-thunk-data', () => ({
  ...jest.requireActual('redux-thunk-data'),
  requestData: config => {
    config.handleSuccess()
    return { type: 'REQUEST_DATA' }
  },
}))

describe('signout button container', () => {
  it('should land to connection page, reset all the store except features', () => {
    // given
    const { store } = configureStore({
      data: {
        bookings: [{ id: 'b1' }],
        features: [{ id: 'f1' }],
        users: [{ id: 'u1' }],
      },
    })
    const history = createBrowserHistory()
    const readRecommendations = [
      { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AE' },
      { dateRead: '2018-12-17T15:59:11.689000Z', id: 'AF' },
    ]

    // when
    mapDispatchToProps(store.dispatch).onSignOutClick(history.push, readRecommendations)()

    // then
    const { data } = store.getState()
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
      searchedRecommendations: [],
      showTypes: [],
      stocks: [],
      types: [],
      users: [],
    })
    expect(history.location.pathname).toBe('/connexion')
  })
})
