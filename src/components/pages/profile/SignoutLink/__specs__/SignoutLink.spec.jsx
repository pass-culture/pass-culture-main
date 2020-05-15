import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'

import Icon from '../../../../layout/Icon/Icon'
import SignoutLink from '../SignoutLink'

describe('signout link', () => {
  let props

  beforeEach(() => {
    props = {
      historyPush: jest.fn(),
      onSignOutClick: jest.fn(),
      readRecommendations: [],
    }
  })

  it('should display one Link and one Icon', () => {
    // given
    const wrapper = shallow(<SignoutLink {...props} />)

    // when
    const link = wrapper.find(Link)
    const icon = wrapper.find(Icon)
    const signoutLabel = wrapper.find({ children: 'Déconnexion' })

    // then
    expect(link).toHaveLength(1)
    expect(icon).toHaveLength(1)
    expect(signoutLabel).toHaveLength(1)
  })

  describe('when clicking on link', () => {
    it('should call the function to sign out', () => {
      // given
      const wrapper = mount(
        <Router history={createBrowserHistory()}>
          <SignoutLink {...props} />
        </Router>
      )
      const signoutLink = wrapper.find({ children: 'Déconnexion' }).parent()

      // when
      signoutLink.invoke('onClick')

      // then
      expect(props.onSignOutClick).toHaveBeenCalledWith(
        props.historyPush,
        props.readRecommendations
      )
    })
  })
})
