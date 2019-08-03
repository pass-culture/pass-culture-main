import React from 'react'
import { shallow } from 'enzyme'

import BookingCancel from '../BookingCancel'

describe('src | components | booking | sub-items | BookingCancel', () => {
  let props

  beforeEach(() => {
    props = {
      data: {
        stock: {
          price: 12,
        },
      },
      isEvent: true,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingCancel {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should render BookingCancel component using informations from props', () => {
    // when
    const wrapper = shallow(<BookingCancel {...props} />)

    // then
    const mainWrapper = wrapper.find('.text-center')
    expect(mainWrapper).toBeDefined()
    const spans = mainWrapper.find('p span')
    expect(spans).toHaveLength(2)
    expect(spans.at(0).text()).toBe('12 € vont être recrédités sur votre pass.')
    expect(spans.at(1).text()).toBe('Vous allez recevoir un e-mail de confirmation.')
  })

  describe('when offer is an event', () => {
    it('should add event className', () => {
      // given
      props.isEvent = true

      // when
      const wrapper = shallow(<BookingCancel {...props} />)

      // then
      const mainWrapper = wrapper.find('.text-center.event')
      expect(mainWrapper).toHaveLength(1)
    })
  })

  describe('when offer is a thing', () => {
    it('should add thing className', () => {
      // given
      props.isEvent = false

      // when
      const wrapper = shallow(<BookingCancel {...props} />)

      // then
      const mainWrapper = wrapper.find('.text-center.thing')
      expect(mainWrapper).toHaveLength(1)
    })
  })
})
