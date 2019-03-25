import React from 'react'
import { shallow } from 'enzyme'
import configureStore from 'redux-mock-store'

import ActivationRoutesContainer from '../ActivationRoutesContainer'
import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../../../hocs/with-login'

jest.mock('../../../hocs/with-login', () => ({
  withRedirectToDiscoveryWhenAlreadyAuthenticated: jest.fn(() => ''),
}))
describe('src | components | pages | activation | tests | ActivationRoutesContainer', () => {
  it('should redirect to discovery page when user is already logged in', () => {
    // given
    const middlewares = []
    const mockStore = configureStore(middlewares)
    const initialState = {}
    const store = mockStore(initialState)

    // when
    shallow(<ActivationRoutesContainer />, { context: { store } })

    // then
    expect(withRedirectToDiscoveryWhenAlreadyAuthenticated).toHaveBeenCalled()
  })
})
