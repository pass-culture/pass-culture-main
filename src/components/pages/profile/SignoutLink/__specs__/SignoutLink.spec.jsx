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
      readRecommendations: [],
      reinitializeDataExceptFeatures: jest.fn(),
      resetSeedLastRequestTimestamp: jest.fn(),
      signOut: jest.fn(),
      updateReadRecommendations: jest.fn(),
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
    describe('when user has not seen any recommendation', () => {
      it('should call functions to sign out and redirect to form connection', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => 1590428424078)
        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <SignoutLink {...props} />
          </Router>
        )
        const signoutLink = wrapper.find({ children: 'Déconnexion' }).parent()

        // when
        signoutLink.invoke('onClick')({ defaultPrevented: jest.fn() })

        // then
        expect(props.updateReadRecommendations).not.toHaveBeenCalled()
        expect(props.signOut).toHaveBeenCalledWith(props.reinitializeDataExceptFeatures)
        expect(props.resetSeedLastRequestTimestamp).toHaveBeenCalledWith(1590428424078)
        expect(props.historyPush).toHaveBeenCalledWith('/connexion')
      })
    })

    describe('when user has seen at least one recommendation', () => {
      it('should update read recommendations and sign out', () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => 1590428424078)
        props.readRecommendations = [
          {
            id: 'GH',
          },
        ]
        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <SignoutLink {...props} />
          </Router>
        )
        const signoutLink = wrapper.find({ children: 'Déconnexion' }).parent()

        // when
        signoutLink.invoke('onClick')({ defaultPrevented: jest.fn() })

        // then
        expect(props.updateReadRecommendations).toHaveBeenCalledWith(
          props.readRecommendations,
          expect.any(Function)
        )
      })
    })
  })
})
