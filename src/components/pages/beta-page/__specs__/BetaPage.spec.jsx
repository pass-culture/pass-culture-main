import React from 'react'
import { shallow } from 'enzyme'

import BetaPage from '../BetaPage'
import { Link } from 'react-router-dom'

describe('src | components | pages | BetaPage', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<BetaPage />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should contain a link to connexion page', () => {
    // when
    const wrapper = shallow(<BetaPage />)
    const link = wrapper.find(Link)

    // then
    expect(link).toHaveLength(1)
    expect(link.prop('id')).toBe('beta-connexion-link')
    expect(link.prop('to')).toBe('/connexion')
  })
})
