import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import Price from '../../../../../layout/Price'
import BookThisLink, { formatOutputPrice } from '../BookThisLink'

describe('src | components | verso | verso-controls | booking | BookThisLink', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = {
      linkDestination: '/path/to/page/',
      priceValue: [0],
    }
    // when
    const wrapper = shallow(<BookThisLink {...props} />)

    const buttonLabel = wrapper.find('.pc-ticket-button-label')
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
    expect(buttonLabel).toHaveLength(1)
    expect(buttonLabel.text()).toStrictEqual("J'y vais!")
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

  describe('formatOutputPrice', () => {
    it('return a component with props', () => {
      // given
      const devise = '€'
      const values = [12, 22]

      // when
      const Component = () => formatOutputPrice(values, devise)
      const wrapper = shallow(<Component />)
      const props = wrapper.props()

      // then
      expect(props).toStrictEqual({
        devise: '€',
        endingPrice: 22,
        startingPrice: 12,
      })
    })
  })
})
