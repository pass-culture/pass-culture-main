import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import { Transition } from 'react-transition-group'
import configureStore from 'redux-mock-store'

import CloseLink from '../../layout/Header/CloseLink'
import Header from '../Header'
import Menu from '../Menu'
import NavLink from '../NavLink'
import SignoutButtonContainer from '../SignoutButtonContainer'
import SimpleLink from '../SimpleLink'
import { getFeaturedRoutes } from '../../router/utils'

jest.mock('../../../reducers/overlay', () => ({
  toggleOverlay: jest.fn(),
}))

describe('src | components | menu | Menu', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {},
      history: {
        goBack: jest.fn(),
        location: {
          pathname: 'fake-url/menu',
        },
      },
      readRecommendations: [],
      routes: getFeaturedRoutes([{ name: 'WEBAPP_SIGNUP' }]),
      toggleOverlay: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Menu {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('componentWillUnmount()', () => {
    it('should call toggleOverlay', () => {
      // given
      const wrapper = shallow(<Menu {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.toggleOverlay).toHaveBeenCalledWith()
    })
  })

  describe('render()', () => {
    it('should open the menu with one CloseLink, one Header, two SimpleLink, five NavLink and one SignoutButton', () => {
      // given
      const history = createBrowserHistory()
      const store = configureStore([])({})
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Menu {...props} />
          </Router>
        </Provider>
      )

      // when
      const transition = wrapper.find(Transition)
      const closeLink = wrapper.find(CloseLink)
      const header = wrapper.find(Header)
      const simpleLink = wrapper.find(SimpleLink)
      const navLink = wrapper.find(NavLink)
      const signoutButtonContainer = wrapper.find(SignoutButtonContainer)

      // then
      expect(transition).toHaveLength(1)
      expect(closeLink).toHaveLength(1)
      expect(header).toHaveLength(1)
      expect(simpleLink).toHaveLength(2)
      expect(navLink).toHaveLength(4)
      expect(signoutButtonContainer).toHaveLength(1)
      expect(props.toggleOverlay).toHaveBeenCalledWith()
    })
  })
})
