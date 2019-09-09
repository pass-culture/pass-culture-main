import React from 'react'
import { shallow } from 'enzyme'

import Icon, { getImageUrl } from '../Icon'

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
    it('should render an image with correct props', () => {
      // when
      const wrapper = shallow(<Icon {...props} />)

      // then
      const image = wrapper.find('img')
      expect(image).toHaveLength(1)
      expect(image.props().alt).toStrictEqual('picto-svg')
      expect(image.props().src).toMatch(/(icons\/picto-svg.svg)/)
    })
  })
})

describe('src | components | layout | Icon | getImageUrl', () => {
  it('url should contains right extension when svg given', () => {
    // given
    const svg = 'icon-profil'

    // when
    const iconUrl = getImageUrl(svg)

    // then
    expect(iconUrl).toMatch(/(icons\/icon-profil.svg)/)
  })

  it('url should contains right extension when png given', () => {
    // given
    const png = 'icon-profil'
    const svg = null

    // when
    const iconUrl = getImageUrl(svg, png)

    // then
    expect(iconUrl).toMatch(/(icons\/icon-profil.png)/)
  })
})
