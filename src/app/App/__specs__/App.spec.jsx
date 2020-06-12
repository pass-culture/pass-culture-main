import { shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { App } from '../App'
import RedirectToMaintenance from '../RedirectToMaintenance/RedirectToMaintenance'
import { StatusBarHelmet } from '../StatusBar/StatusBarHelmet'

const middlewares = []
const mockStore = configureStore(middlewares)

jest.mock('../../../styles/variables/index.scss', () => {
  return { primary: 'primaryColor', black: 'defaultColor' }
})

describe('src | components | App', () => {
  it('should match the snapshot', () => {
    // given
    const initialState = {}
    const store = mockStore(initialState)
    const props = {
      children: <div />,
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
      children: <div />,
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

  it('should render a StatusBarHelmet component', () => {
    // Given
    const props = {
      children: <div />,
      history: {},
      isMaintenanceActivated: false,
      location: {
        pathname: '/discovery',
      },
    }

    // When
    const wrapper = shallow(<App {...props} />)

    // Then
    const statusBarComponent = wrapper.find(StatusBarHelmet)
    expect(statusBarComponent).toHaveLength(1)
    expect(statusBarComponent.prop('pathname')).toBe('/discovery')
  })
})
