// jest --env=jsdom ./src/components/verso/verso-buttons/tests/BookThisButton --watch
import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'

import BookThisButton from '../BookThisButton'

describe('src | components | verso | verso-buttons | BookThisButton', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = {
      linkDestination: '/path/to/page/',
      priceValue: [0],
    }

    // when
    const wrapper = shallow(<BookThisButton {...props} />)

    // then
    const buttonLabel = wrapper.find('.button-label')
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
    expect(buttonLabel).toHaveLength(1)
    expect(buttonLabel.text()).toEqual("J'y vais!")
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
        <BookThisButton {...props} />
      </MemoryRouter>
    )

    // then
    const price = wrapper.find('.price')
    expect(price).toHaveLength(1)
    expect(price.text()).toEqual('Gratuit')
  })

  it('should render a price range when multiples prices are given', () => {
    // given
    const props = {
      linkDestination: '/path/to/page',
      priceValue: [0, 30, 10],
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <BookThisButton {...props} />
      </MemoryRouter>
    )
    const price = wrapper.find('.price')

    // then
    expect(price).toHaveLength(1)
    expect(price.text()).toEqual('0 \u2192 30 €')
  })
})
