import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'
import { App } from '../App'
import RedirectToMaintenance from '../RedirectToMaintenance'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | App', () => {
  it('should match the snapshot', () => {
    // given
    const initialState = {}
    const store = mockStore(initialState)
    const props = {
      location: {},
    }

    // when
    const wrapper = shallow(
      <Provider store={store}>
        <App {...props} />
      </Provider>
    )

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a Redirect component when isMaintenanceSelector.js is true', () => {
    // given
    const props = {
      history: {},
      location: {},
      isMaintenanceActivated: true,
    }
    // when
    const wrapper = shallow(
      <App {...props}>
        <p>
          {'Sub component'}
        </p>
      </App>
    )

    // then
    const redirectNode = wrapper.find(RedirectToMaintenance)
    expect(redirectNode).toHaveLength(1)
  })
})
