import { shallow } from 'enzyme'
import React from 'react'

import Price from '../Price'

describe('src | components | Price', () => {
  const NO_BREAK_SPACE = '\u00A0'

  it('should display a price', () => {
    // given
    const props = { value: 5 }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    const price = wrapper.find({ children: `5${NO_BREAK_SPACE}€` })
    expect(price).toHaveLength(1)
  })

  it('should display a range of prices', () => {
    // given
    const props = { value: [5, 10] }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    const price = wrapper.find({ children: `5 → 10${NO_BREAK_SPACE}€` })
    expect(price).toHaveLength(1)
  })

  it('should display a range of decimal prices', () => {
    // given
    const props = { value: [5.99, 10] }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    const price = wrapper.find({ children: `5,99 → 10${NO_BREAK_SPACE}€` })
    expect(price).toHaveLength(1)
  })

  it('should display zero euro', () => {
    // given
    const props = { value: 0 }

    // when
    const wrapper = shallow(<Price {...props} />)

    // then
    const price = wrapper.find({ children: `0${NO_BREAK_SPACE}€` })
    expect(price).toHaveLength(1)
  })
})
