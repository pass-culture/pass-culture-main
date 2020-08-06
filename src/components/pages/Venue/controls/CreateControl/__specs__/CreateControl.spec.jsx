import { shallow } from 'enzyme'
import React from 'react'
import { NavLink } from 'react-router-dom'

import CreateControl from '../CreateControl'

describe('src | components | pages | Venue | controls | CreateControl ', () => {
  let props

  beforeEach(() => {
    props = {
      venueId: '1',
      offererId: 'RG',
    }
  })

  describe('render', () => {
    it('should display a create offer in the venue link', () => {
      // when
      const wrapper = shallow(<CreateControl {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      const spanText = navLink.find('span')

      expect(navLink.prop('className')).toBe('button is-tertiary is-medium')
      expect(spanText.text()).toBe('Créer une offre dans ce lieu')
      expect(navLink.prop('to')).toBe('/offres/creation?lieu=1&structure=RG')
    })
  })
})
