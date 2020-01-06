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
      children: (<div />),
      history: {},
      isMaintenanceActivated: false,
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

  it('should render a RedirectToMaintenance component when maintenance mode is activated', () => {
    // given
    const props = {
      children: (<div />),
      history: {},
      isMaintenanceActivated: true,
      location: {},
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
    const redirectToMaintenance = wrapper.find(RedirectToMaintenance)
    expect(redirectToMaintenance).toHaveLength(1)
  })
})
