import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Link, Router } from 'react-router-dom'
import { Transition } from 'react-transition-group'
import configureStore from 'redux-mock-store'

import CloseLink from '../../Header/CloseLink/CloseLink'
import Header from '../Header/Header'
import Menu from '../Menu'
import MenuItem from '../MenuItem/MenuItem'
import SignoutButtonContainer from '../SignoutButton/SignoutButtonContainer'

jest.mock('../../../../reducers/overlay', () => ({
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
      toggleOverlay: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Menu {...props} />)

    // then
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
      const initialState = { data: { features: [] } }
      const store = configureStore([])(initialState)
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
      const anchor = wrapper.find(MenuItem).find('a')
      const link = wrapper.find(MenuItem).find(Link)
      const signoutButtonContainer = wrapper.find(SignoutButtonContainer)

      // then
      expect(transition).toHaveLength(1)
      expect(closeLink).toHaveLength(1)
      expect(header).toHaveLength(1)
      expect(anchor).toHaveLength(7)
      expect(link).toHaveLength(5)
      expect(signoutButtonContainer).toHaveLength(1)
      expect(props.toggleOverlay).toHaveBeenCalledWith()
    })
  })
})
