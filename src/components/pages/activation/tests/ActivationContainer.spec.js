import { shallow } from 'enzyme'
import React from 'react'
import configureStore from 'redux-mock-store'

import ActivationContainer from '../ActivationContainer'
import { withNotRequiredLogin } from '../../../hocs'

jest.mock('../../../hocs/with-login', () => ({
  withNotRequiredLogin: jest.fn(() => ''),
}))

describe('src | components | pages | activation | ActivationContainer', () => {
  it('should redirect to discovery page when user is already logged in', () => {
    // given
    const middlewares = []
    const mockStore = configureStore(middlewares)
    const initialState = {}
    const store = mockStore(initialState)

    // when
    shallow(<ActivationContainer />, { context: { store } })

    // then
    expect(withNotRequiredLogin).toHaveBeenCalledWith(expect.any(Function))
  })
})
