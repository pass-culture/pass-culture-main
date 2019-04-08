import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router-dom'

import { RawSignupPage } from '../SignupPage'
import { configureStore } from '../../../utils/store'

const mockRequestDataCatch = jest.fn()
jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')
  return {
    ...actualModule,
    requestData: config => {
      mockRequestDataCatch(config)
      return actualModule.requestData(config)
    },
  }
})

describe('src | components | pages | SignupPage', () => {
  it('should call users/signup/webapp', () => {
    // given
    fetch.mockResponse(JSON.stringify({}), { status: 200 })
    const { store } = configureStore()
    const history = createBrowserHistory()
    const values = {
      contact_ok: true,
      email: 'fake@email.fr',
      password: 'fake.P@ssw0rd',
      publicName: 'fakePublic',
    }
    const wrapper = mount(
      <Provider store={store}>
        <Router history={history}>
          <Route path="/test">
            <RawSignupPage />
          </Route>
        </Router>
      </Provider>
    )
    wrapper
      .find("input[name='email']")
      .simulate('change', { target: { value: values.email } })
    wrapper
      .find("input[name='password']")
      .simulate('change', { target: { value: values.password } })
    wrapper
      .find("input[name='publicName']")
      .simulate('change', { target: { value: values.publicName } })
    wrapper
      .find("input[name='contact_ok']")
      .simulate('change', { target: { checked: true } })

    const expectedSubConfig = {
      apiPath: 'users/signup/webapp',
      body: values,
      method: 'POST',
      name: 'user',
      normalizer: null,
    }
    // when
    const submitButton = wrapper.find('button[name="user"]')

    // then
    expect(submitButton.props().disabled).toEqual(false)

    // when
    submitButton.simulate('click')

    // then
    const receivedConfig = mockRequestDataCatch.mock.calls[0][0]
    Object.keys(expectedSubConfig).forEach(key =>
      expect(receivedConfig[key]).toEqual(expectedSubConfig[key])
    )
  })
})
