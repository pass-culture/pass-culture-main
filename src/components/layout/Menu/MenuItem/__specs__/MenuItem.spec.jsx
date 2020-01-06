import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import MenuItem from '../MenuItem'
import Item from '../Item/Item'

describe('src | components | menu | MenuItem', () => {
  let props

  beforeEach(() => {
    props = {
      isDisabled: false,
      item: {
        icon: 'offres-w',
        path: '/plop',
        title: 'Fake title',
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<MenuItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a router Link and an Item when no href', () => {
      // given
      const wrapper = shallow(<MenuItem {...props} />)

      // when
      const link = wrapper.find(Link)
      const item = wrapper.find(Item)

      // then
      expect(link).toHaveLength(1)
      expect(item).toHaveLength(1)
    })

    it('should render a standard HTML link and an Item when href', () => {
      // given
      props.item.href = 'https://foo.com'
      props.item.target = '_blank'
      const wrapper = shallow(<MenuItem {...props} />)

      // when
      const link = wrapper.find('a')
      const item = wrapper.find(Item)

      // then
      expect(link).toHaveLength(1)
      expect(item).toHaveLength(1)
    })

    it('should render a link with no rel if target not equal blank', () => {
      // given
      props.item.href = 'https://foo.com'
      props.item.target = 'plop'
      const wrapper = shallow(<MenuItem {...props} />)

      // when
      const { rel } = wrapper.find('a').props()

      // then
      expect(rel).toBeNull()
    })

    it('should not render anything if feature is disabled', () => {
      // given
      props.isDisabled = true

      // when
      const wrapper = shallow(<MenuItem {...props} />)

      // then
      expect(wrapper.html()).toBeNull()
    })
  })
})
