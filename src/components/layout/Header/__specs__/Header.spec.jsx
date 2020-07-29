import React from 'react'
import { shallow } from 'enzyme'

import Header from '../Header'
import Icon from '../../Icon'

describe('src | components | Layout | Header', () => {
  let props

  beforeEach(() => {
    props = {
      isSmall: false,
      name: 'fake name',
      offerers: [{}],
      whiteHeader: false,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Header {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a header element with the right css classes when is not small', () => {
      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('navbar is-primary')
    })

    it('should render a header element with the right css classes when is small', () => {
      // given
      props.isSmall = true

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('navbar is-primary is-small')
    })

    describe('should pluralize offerers menu link', () => {
      it('should display Structure juridique when one offerer', () => {
        // when
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')

        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(7)
        expect(linkTitle).toStrictEqual('Structure juridique')
      })

      it('should display Structures juridiques when many offerers', () => {
        // given
        props.offerers = [{}, {}]

        // when
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')
        const linkTitle = navLinks
          .at(4)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(7)
        expect(linkTitle).toStrictEqual('Structures juridiques')
      })
    })

    describe('help link', () => {
      it('should display a "help" link in the header', () => {
        // when
        const wrapper = shallow(<Header {...props} />)

        // then
        const helpLink = wrapper
          .find('.navbar-menu')
          .find('.navbar-end')
          .find('.navbar-item')
          .at(2)
        expect(helpLink.prop('href')).toBe(
          'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
        )
        expect(helpLink.prop('target')).toBe('_blank')
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
