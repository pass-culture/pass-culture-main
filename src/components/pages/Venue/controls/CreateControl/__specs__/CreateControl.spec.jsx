import { shallow } from 'enzyme'
import React from 'react'
import CreateControl from '../CreateControl'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | Venue | controls | CreateControl ', () => {
  let props

  beforeEach(() => {
    props = {
      venueId: 1,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<CreateControl {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should display a NavLink component with the right props', () => {
      // when
      const wrapper = shallow(<CreateControl {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink.prop('className')).toBe('button is-secondary is-medium')
      expect(navLink.prop('to')).toBe('/offres/creation?lieu=1')
    })
  })
})
