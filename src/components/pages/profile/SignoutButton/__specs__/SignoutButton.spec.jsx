import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import SignoutButton from '../SignoutButton'
import Icon from '../../../../layout/Icon/Icon'

describe('signout button', () => {
  let props

  beforeEach(() => {
    props = {
      historyPush: jest.fn(),
      onSignOutClick: jest.fn(),
      readRecommendations: [],
    }
  })

  it('should display one button and 2 Icons', () => {
    // given
    const wrapper = shallow(<SignoutButton {...props} />)

    // when
    const link = wrapper.find(Link)
    const icon = wrapper.find(Icon)
    const signoutLabel = wrapper.find({ children: 'Déconnexion' })

    // then
    expect(link).toHaveLength(1)
    expect(icon).toHaveLength(2)
    expect(signoutLabel).toHaveLength(1)
  })
})
