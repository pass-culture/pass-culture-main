import React from 'react'
import { shallow } from 'enzyme'

import Icon from '../Icon'

describe('src | components | layout | Icon ', () => {
  let props

  beforeEach(() => {
    props = {
      svg: 'picto-svg',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Icon {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render an image with correct props when svg given', () => {
      // when
      const wrapper = shallow(<Icon {...props} />)

      // then
      const image = wrapper.find('img')
      expect(image).toHaveLength(1)
      expect(image.props().alt).toStrictEqual('picto-svg')
      expect(image.props().src).toMatch(/(icons\/picto-svg.svg)/)
    })

    it('should render an image with correct props when png given', () => {
      // when
      props.png = 'icon-png'
      props.svg = null
      const wrapper = shallow(<Icon {...props} />)

      // then
      const image = wrapper.find('img')
      expect(image).toHaveLength(1)
      expect(image.props().alt).toStrictEqual('icon-png')
      expect(image.props().src).toMatch(/(icons\/icon-png.png)/)
    })
  })
})
