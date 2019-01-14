import React from 'react'
import { shallow } from 'enzyme'

import RawHeader from '../RawHeader'

describe('src | components | Layout | RawHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        name: 'Fake Name',
        offerers: [{}],
      }

      // when
      const wrapper = shallow(<RawHeader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('should pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        const props = {
          offerers: [{}],
        }

        // when
        const wrapper = shallow(<RawHeader {...props} />)
        const navLinks = wrapper.find('NavLink')

        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(5)
        expect(linkTitle).toEqual('Votre structure')
      })
      it('should display Vos structures when many offerers', () => {
        // given
        const props = {
          offerers: [{}, {}],
        }

        // when
        const wrapper = shallow(<RawHeader {...props} />)
        const navLinks = wrapper.find('NavLink')

        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(5)
        expect(linkTitle).toEqual('Vos structures')
      })
    })
  })
})
