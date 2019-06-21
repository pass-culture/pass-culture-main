import { shallow } from 'enzyme'
import React from 'react'

import Icon from '../../layout/Icon'
import Item from '../Item'

describe('src | components | menu | Item', () => {
  let props

  beforeEach(() => {
    props = {
      icon: 'offres-w',
      title: 'Fake title',
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Item {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render one Icon and one title', () => {
      // given
      const wrapper = shallow(<Item {...props} />)

      // when
      const span = wrapper.find('span')
      const icon = wrapper.find(Icon)

      // then
      const title = span.at(1).text()
      expect(span).toHaveLength(2)
      expect(icon).toHaveLength(1)
      expect(title).toBe('Fake title')
    })
  })
})
