import React from 'react'
import { shallow } from 'enzyme'
import Venues from '../Venues'

describe('src | components | pages | OffererCreation | Venues', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: '5767Fdtre',
      venues: [],
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Venues {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a title link', () => {
      // given
      props.adminUserOfferer = true
      const wrapper = shallow(<Venues {...props} />)

      // when
      const title = wrapper.find('h2')

      // then
      expect(title.text()).toBe('Lieux')
    })
    it('should render a create venue link', () => {
      // given
      props.adminUserOfferer = true
      const wrapper = shallow(<Venues {...props} />)

      // when
      const navLink = wrapper.find('NavLink')

      // then
      expect(navLink.props().to).toBe('/structures/5767Fdtre/lieux/creation')
    })
  })
})
