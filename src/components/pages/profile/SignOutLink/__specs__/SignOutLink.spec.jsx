import { mount, shallow } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import { Link } from 'react-router-dom'

import Icon from '../../../../layout/Icon/Icon'
import SignOutLink from '../SignOutLink'

describe('sign out link', () => {
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
    const wrapper = shallow(<SignOutLink {...props} />)

    // when
    const link = wrapper.find(Link)
    const icon = wrapper.find(Icon)
    const signOutLabel = wrapper.find({ children: 'Déconnexion' })

    // then
    expect(link).toHaveLength(1)
    expect(icon).toHaveLength(1)
    expect(signOutLabel).toHaveLength(1)
  })

  describe('when clicking on link', () => {
    describe('when user has not seen any recommendation', () => {
      it('should call functions to sign out and redirect to form connection', async () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => 1590428424078)
        const wrapper = mount(
          <MemoryRouter>
            <SignOutLink {...props} />
          </MemoryRouter>
        )
        const signOutLink = wrapper.find({ children: 'Déconnexion' }).parent()

        // when
        await signOutLink.invoke('onClick')({ defaultPrevented: jest.fn() })

        // then
        expect(props.updateReadRecommendations).not.toHaveBeenCalled()
        expect(props.signOut).toHaveBeenCalledTimes(1)
        expect(props.historyPush).toHaveBeenCalledWith('/connexion')
        expect(props.resetSeedLastRequestTimestamp).toHaveBeenCalledWith(1590428424078)
        expect(props.reinitializeDataExceptFeatures).toHaveBeenCalledTimes(1)
      })
    })

    describe('when user has seen at least one recommendation', () => {
      it('should update read recommendations and sign out', async () => {
        // given
        jest.spyOn(Date, 'now').mockImplementation(() => 1590428424078)
        props.readRecommendations = [
          {
            id: 'GH',
          },
        ]
        const wrapper = mount(
          <MemoryRouter>
            <SignOutLink {...props} />
          </MemoryRouter>
        )
        const signOutLink = wrapper.find({ children: 'Déconnexion' }).parent()

        // when
        await signOutLink.invoke('onClick')({ defaultPrevented: jest.fn() })

        // then
        expect(props.updateReadRecommendations).toHaveBeenCalledWith(props.readRecommendations)
        expect(props.signOut).toHaveBeenCalledTimes(1)
      })
    })
  })
})
