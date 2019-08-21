import React from 'react'
import { shallow } from 'enzyme'

import BookingCancel from '../BookingCancel'

const NO_BREAK_SPACE = '\u00A0'

describe('src | components | layout | Booking | BookingCancel', () => {
  let props

  beforeEach(() => {
    props = {
      data: {
        amount: 12,
      },
      isEvent: true,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<BookingCancel {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render BookingCancel component using informations from props', () => {
    // when
    const wrapper = shallow(<BookingCancel {...props} />)

    // then
    const mainWrapper = wrapper.find('.text-center')
    const spans = mainWrapper.find('p span')
    expect(spans).toHaveLength(2)
    expect(spans.at(0).text()).toBe(`12${NO_BREAK_SPACE}€ vont être recrédités sur votre pass.`)
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
