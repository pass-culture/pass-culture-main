import React from 'react'
import { shallow } from 'enzyme'

import Insert from '../Insert'

describe('src | components | layout | Insert', () => {
  let props

  beforeEach(() => {
    props = {
      children: 'Some fake text',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Insert {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render an Icon', () => {
      // when
      const wrapper = shallow(<Insert {...props} />)

      // then
      const icon = wrapper.find('Icon')
      expect(icon).toHaveLength(1)
    })
  })
})
