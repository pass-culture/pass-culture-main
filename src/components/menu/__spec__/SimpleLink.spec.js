import { shallow } from 'enzyme'
import React from 'react'

import Item from '../Item'
import SimpleLink from '../SimpleLink'

describe('src | components | menu | SimpleLink', () => {
  let props

  beforeEach(() => {
    props = {
      item: {
        href: '/decouverte',
        icon: 'offres-w',
        target: '_blank',
        title: 'Decouverte',
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<SimpleLink {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render one link and one Item', () => {
      // given
      const wrapper = shallow(<SimpleLink {...props} />)

      // when
      const link = wrapper.find('a')
      const item = wrapper.find(Item)

      // then
      expect(link).toHaveLength(1)
      expect(item).toHaveLength(1)
    })

    it('should render a link with no rel if target equal blank', () => {
      // given
      props.item.target = 'plop'
      const wrapper = shallow(<SimpleLink {...props} />)

      // when
      const { rel } = wrapper.find('a').props()

      // then
      expect(rel).toBeNull()
    })
  })
})
