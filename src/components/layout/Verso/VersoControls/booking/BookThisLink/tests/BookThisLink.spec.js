import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import Price from '../../../../../Price'
import BookThisLink from '../BookThisLink'

describe('src | components | verso | verso-controls | booking | BookThisLink', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = {
      isFinished: false,
      location: {
        search: '',
      },
      match: {
        params: {},
        url: '/decouverte',
      },
      priceRange: [10, 30],
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
      isFinished: false,
      location: {
        search: '',
      },
      match: {
        params: {},
        url: '/decouverte',
      },
      priceRange: [0],
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
    const minPrice = 10
    const maxPrice = 30
    const props = {
      isFinished: false,
      location: {
        search: '',
      },
      match: {
        params: {},
        url: '/decouverte',
      },
      priceRange: [minPrice, maxPrice],
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
    expect(price.text()).toStrictEqual(`${minPrice}${nbsp}${arrow}${nbsp}${maxPrice}${nbsp}€`)
  })

  describe('getLinkDestination', () => {
    it('should add reservations to current url without query to open booking card', () => {
      // given
      const mediationId = 'CG'
      const offerId = 'BF'
      const pathname = '/decouverte'
      const search = '?foo'
      const props = {
        isFinished: false,
        location: {
          pathname,
          search,
        },
        match: {
          params: {},
          url: `/decouverte/${offerId}/${mediationId}`,
        },
        priceRange: [],
      }
      const expected = `${pathname}/${offerId}/${mediationId}/reservation${search}`

      // when
      const wrapper = shallow(<BookThisLink {...props} />)
      const result = wrapper.instance().getLinkDestination()

      // then
      expect(result).toStrictEqual(expected)
    })

    it('should not add reservations to current url if bookings already in match params', () => {
      // given
      const mediationId = 'CG'
      const offerId = 'BF'
      const pathname = '/decouverte'
      const search = '?foo'
      const url = `http://${pathname}/${offerId}/${mediationId}/reservation${search}`
      const props = {
        isFinished: false,
        location: {
          pathname,
          search,
        },
        match: {
          params: {
            bookings: 'reservations',
          },
          url,
        },
        priceRange: [],
      }
      const expected = url

      // when
      const wrapper = shallow(<BookThisLink {...props} />)
      const result = wrapper.instance().getLinkDestination()

      // then
      expect(result).toStrictEqual(expected)
    })
  })
})
