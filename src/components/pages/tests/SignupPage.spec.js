// jest --env=jsdom ./src/components/pages/tests/SignupPage --watch
/* eslint-disable */
import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React, { Component } from 'react'
import { connect, Provider } from 'react-redux'
import { Route, Router } from 'react-router-dom'
import configureStore from 'redux-mock-store'

import { RawSignupPage } from '../SignupPage'

const mockStore = configureStore([])
class RawFormCallback extends Component {
  componentDidUpdate() {
    const { onFormUpdate } = this.props
    onFormUpdate()
  }

  render() {
    return null
  }
}
function mapStateToProps(state) {
  return { form: state.form.user }
}
const FormCallback = connect(mapStateToProps)(RawFormCallback)

describe('src | components | pages | SignupPage', () => {
  it('should call users/signup/webapp', done => {
    // given
    function setInput(wrapper, key, value) {
      wrapper
        .find(`input[name='${key}']`)
        .simulate('change', { target: { value } })
    }
    const mockDispatch = jest.fn()
    const failFunction = jest.fn()
    const initialState = { data: { users: [] }, form: { user: {} }, modal: {} }
    const store = mockStore(initialState)
    const successFunction = jest.fn()
    const values = {
      contact_ok: true,
      email: 'fake@email.fr',
      password: 'fake.P@ssw0rd',
      publicName: 'fakePublic',
    }
    const props = { dispatch: mockDispatch }
    const history = createBrowserHistory()
    history.push('/test')
    const wrapper = mount(
      <Provider store={store}>
        <Router history={history}>
          <Route path="/test">
            <RawSignupPage {...props} />
            <FormCallback onFormUpdate={onFormUpdate} />
          </Route>
        </Router>
      </Provider>
    )
    Object.keys(values).forEach(key => setInput(wrapper, key, values[key]))
    /* eslint-disable no-use-before-define */
    function onFormUpdate() {
      const config = {
        apiPath: '/users/signup/webapp',
        body: values,
        handleFail: failFunction,
        handleSuccess: successFunction,
        method: 'POST',
      }
      const expectedAction = {
        config,
        type: 'REQUEST_DATA_POST_/USERS/SIGNUP/WEBAPP',
      }

      // when
      const submitButton = wrapper.find('button[name="user"]')

      // then
      console.log(submitButton.props())
      expect(submitButton.props().disabled).toEqual(false)
      submitButton.simulate('click')
      expect(mockDispatch).toHaveBeenCalledWith(expectedAction)
      done()
    }
  })
})
