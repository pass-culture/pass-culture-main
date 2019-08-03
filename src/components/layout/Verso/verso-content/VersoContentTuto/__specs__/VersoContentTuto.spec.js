import React from 'react'
import { shallow } from 'enzyme'

import VersoContentTuto from '../VersoContentTuto'

describe('src | components | verso | verso-content | VersoContentTuto', () => {
  it('should match the snapshot', () => {
    // given
    const props = { imageURL: 'https://example.net/img.jpg' }

    // when
    const wrapper = shallow(<VersoContentTuto {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should have a classnamed element with sourced img', () => {
    // given
    const props = { imageURL: 'https://example.net/img.jpg' }

    // when
    const wrapper = shallow(<VersoContentTuto {...props} />)
    const img = wrapper.find('img')

    // then
    expect(img).toHaveLength(1)
    expect(img.hasClass('verso-tuto-mediation')).toBe(true)
    expect(img.prop('src')).toStrictEqual('https://example.net/img.jpg')
  })
})
