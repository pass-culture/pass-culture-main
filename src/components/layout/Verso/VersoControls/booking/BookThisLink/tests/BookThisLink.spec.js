import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import Price from '../../../../../Price'
import BookThisLink from '../BookThisLink'

describe('src | components | verso | verso-controls | booking | BookThisLink', () => {
  let props

  beforeEach(() => {
    props = {
      destinationLink: 'fake/url',
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
  })

  it('should match snapshot with required props', () => {
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
    props.priceRange = [0]

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
    // when
    const wrapper = mount(
      <MemoryRouter>
        <BookThisLink {...props} />
      </MemoryRouter>
    )

    // then
    const priceComponent = wrapper.find(Price)
    expect(priceComponent).toHaveLength(1)
  })
})
