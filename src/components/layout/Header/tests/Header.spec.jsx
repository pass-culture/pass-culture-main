import React from 'react'
import { shallow } from 'enzyme'

import Header from '../Header'
import { Icon } from 'components/layout/Icon'

describe('src | components | Layout | Header', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        name: 'Fake Name',
        offerers: [{}],
      }

      // when
      const wrapper = shallow(<Header {...props} />)

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
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')

        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(6)
        expect(linkTitle).toEqual('Votre structure juridique')
      })

      it('should display Vos structures when many offerers', () => {
        // given
        const props = {
          offerers: [{}, {}],
        }

        // when
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')
        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(6)
        expect(linkTitle).toEqual('Vos structures juridiques')
      })
    })

    describe('help link', () => {
      const props = {
        offerers: [{}, {}],
      }

      it('should display a "help" link in the header', () => {
        // when
        const wrapper = shallow(<Header {...props} />)

        // then
        const helpLink = wrapper
          .find('.navbar-menu')
          .find('.navbar-end')
          .find('.navbar-item')
          .at(2)
        expect(helpLink).toBeDefined()
        expect(helpLink.prop('href')).toBe(
          'https://docs.passculture.app/structures-culturelles'
        )
      })

      it('should display a "help" icon and the proper label', () => {
        // when
        const wrapper = shallow(<Header {...props} />)

        // then
        const helpLink = wrapper
          .find('.navbar-menu')
          .find('.navbar-end')
          .find('.navbar-item')
          .at(2)
        const spans = helpLink.find('span')
        const helpIcon = spans.at(0).find(Icon)
        const helpLabel = spans.at(1)
        expect(helpIcon.prop('svg')).toBe('ico-help-w')
        expect(helpLabel.text()).toBe('Aide')
      })
    })
  })
})
