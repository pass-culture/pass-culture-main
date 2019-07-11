import React from 'react'
import { shallow } from 'enzyme'
import VersoPriceFormatter from '../VersoPriceFormatter'

describe('src | components | VersoPriceFormatter', () => {
  it('should match snapshot with required price', () => {
    // given
    const props = {
      devise: 'poires',
      endingPrice: undefined,
      startingPrice: 42,
    }

    // when
    const wrapper = shallow(<VersoPriceFormatter {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should a single formatted price', () => {
    // given
    const nbsp = '\u00a0'
    const props = {
      devise: 'poires',
      startingPrice: 12,
    }

    // when
    const wrapper = shallow(<VersoPriceFormatter {...props} />)

    // then
    expect(wrapper.text()).toStrictEqual(`12${nbsp}poires`)
  })

  it('should return a multi formatted price', () => {
    // given
    const nbsp = '\u00a0'
    const arrow = '\u27A4'
    const props = {
      devise: 'poires',
      endingPrice: 22,
      startingPrice: 12,
    }

    // when
    const wrapper = shallow(<VersoPriceFormatter {...props} />)

    // then
    expect(wrapper.text()).toStrictEqual(`12${nbsp}${arrow}${nbsp}22${nbsp}poires`)
  })
})
