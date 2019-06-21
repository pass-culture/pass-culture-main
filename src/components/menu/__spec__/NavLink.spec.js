import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import Item from '../Item'
import NavLink from '../NavLink'

describe('src | components | menu | NavLink', () => {
  let props

  beforeEach(() => {
    props = {
      item: {
        icon: 'offres-w',
        path: '/plop',
        title: 'Fake title',
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<NavLink {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render one Link and one Item', () => {
      // given
      const wrapper = shallow(<NavLink {...props} />)

      // when
      const link = wrapper.find(Link)
      const item = wrapper.find(Item)

      // then
      expect(link).toHaveLength(1)
      expect(item).toHaveLength(1)
    })

    it('should render a link with no rel if target equal blank', () => {
      // given
      props.item.path = '/decouverte/:plop'
      const wrapper = shallow(<NavLink {...props} />)

      // when
      const { to } = wrapper.find(Link).props()

      // then
      expect(to).toBe('/')
    })
  })
})
