import React from 'react'
import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'

import VenueItem from '../VenueItem'
import { Router, NavLink } from 'react-router-dom'

describe('src | components | pages | Offerer | VenueItem', () => {
  let props
  let history

  beforeEach(() => {
    props = {
      venue: {
        id: 'AAA',
        managingOffererId: 'ABC',
        name: 'fake name',
        publicName: null,
      },
    }
    history = createBrowserHistory()
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<VenueItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should render component with venue name when no public name provided', () => {
      // given

      // when
      const wrapper = mount(
        <Router history={history}>
          <VenueItem {...props} />
        </Router>
      )

      // then
      const venueName = wrapper.find('.name')
      const navLink = venueName.find(NavLink)
      expect(venueName.text()).toBe('fake name')
      expect(navLink.prop('id')).toBe('a-fake-name')
      expect(navLink.prop('to')).toBe('/structures/ABC/lieux/AAA')
    })

    it('should render component with venue public name when public name provided', () => {
      // given
      props.venue.publicName = 'fake public name'

      // when
      const wrapper = mount(
        <Router history={history}>
          <VenueItem {...props} />
        </Router>
      )

      // then
      const venueName = wrapper.find('.name')
      const navLink = venueName.find(NavLink)
      expect(venueName.text()).toBe('fake public name')
      expect(navLink.prop('id')).toBe('a-fake-public-name')
    })
  })
})
