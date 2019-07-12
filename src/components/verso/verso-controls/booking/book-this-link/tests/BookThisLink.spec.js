import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import Price from '../../../../../layout/Price'
import BookThisLink from '../BookThisLink'
import VersoPriceFormatter from '../../verso-price-formatter/VersoPriceFormatter'

describe('src | components | verso | verso-controls | booking | BookThisLink', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = {
      linkDestination: '/path/to/page/',
      priceValue: [0],
    }

    // when
    const wrapper = shallow(<BookThisLink {...props} />)

    // then
    const buttonLabel = wrapper.find('.pc-ticket-button-label')
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
    expect(buttonLabel).toHaveLength(1)
    expect(buttonLabel.text()).toBe('J’y vais !')
  })

  it('should render Gratuit label when price value is 0', () => {
    // given
    const props = {
      linkDestination: '/path/to/page',
      priceValue: [0],
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <BookThisLink {...props} />
      </MemoryRouter>
    )

    // then
    const priceComponent = wrapper.find(Price)
    expect(priceComponent).toHaveLength(1)
    expect(priceComponent.hasClass('pc-ticket-button-price')).toBe(true)
    const price = wrapper.find('.price')

    // then
    expect(price).toHaveLength(1)
    expect(price.text()).toStrictEqual('Gratuit')
  })

  it('should render a price range when multiples prices are given', () => {
    // given
    const nbsp = '\u00a0'
    const arrow = '\u27A4'
    const props = {
      linkDestination: '/path/to/page',
      priceValue: [0, 30, 10],
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <BookThisLink {...props} />
      </MemoryRouter>
    )

    // then
    const priceComponent = wrapper.find(Price)
    expect(priceComponent).toHaveLength(1)
    expect(priceComponent.hasClass('pc-ticket-button-price')).toBe(true)

    // then
    const price = wrapper.find('.price')
    expect(price).toHaveLength(1)
    expect(price.text()).toStrictEqual(`0${nbsp}${arrow}${nbsp}30${nbsp}€`)
  })
})
