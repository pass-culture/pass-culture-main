import React from 'react'
import { shallow, mount } from 'enzyme'

import BookingCancellation from '../BookingCancellation'

describe('src | components | layout | BookingCancellation | BookingCancellation', () => {
  let props

  beforeEach(() => {
    props = {
      booking: {
        amount: 23,
      },
      history: {
        replace: jest.fn(),
      },
      match: {
        url: 'http:/AEEA/3M/details/reservation/WY/annulation/confirmation',
      },
      offer: {
        isEvent: true,
        name: 'Mon Offre',
        venue: {
          name: 'Ma venue',
        },
      },
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingCancellation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should redirect to details page', () => {
    // given
    const wrapper = mount(<BookingCancellation {...props} />)
    const okButton = wrapper.find('#booking-cancellation-confirmation-button')

    // when
    okButton.simulate('click')

    // then
    expect(props.history.replace.mock.calls[0][0]).toStrictEqual('http:/AEEA/3M/details')
  })
})
