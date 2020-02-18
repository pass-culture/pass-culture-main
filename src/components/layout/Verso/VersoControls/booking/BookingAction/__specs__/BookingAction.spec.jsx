import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import BookingAction from '../BookingAction'
import BookingActionContainer from '../BookingActionContainer'
import getMockStore from '../../../../../../../utils/mockStore'
import Price from '../../../../../Price/Price'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

describe('components | BookingAction', () => {
  let props

  beforeEach(() => {
    props = {
      bookingUrl: 'http://booking-layout.com',
      history: {
        push: jest.fn(),
      },
      offerCannotBeBooked: false,
      priceRange: [10, 30],
    }
  })

  it('should render a clickable button when offer is bookable', () => {
    // given
    props.offerCannotBeBooked = false

    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    expect(wrapper.prop('className')).toBe('ticket-action')
    expect(wrapper.prop('disabled')).toBe(false)
    expect(wrapper.prop('onClick')).toStrictEqual(expect.any(Function))
    expect(wrapper.prop('type')).toBe('button')
  })

  it('should render a not clickable button when offer is not bookable', () => {
    // given
    props.offerCannotBeBooked = true

    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    expect(wrapper.prop('disabled')).toBe(true)
  })

  it('should render a price and label within link', () => {
    // when
    const wrapper = shallow(<BookingAction {...props} />)

    // then
    const price = wrapper.find(Price)
    expect(price).toHaveLength(1)
    expect(price.prop('className')).toBe('ticket-price')
    expect(price.prop('free')).toBe('Gratuit')
    expect(price.prop('value')).toStrictEqual([10, 30])
  })

  describe('when I click on button for booking', () => {
    it('should render the booking layout', () => {
      // given
      const mockHistory = createMemoryHistory()
      mockHistory.push('/decouverte?param=value')
      const mockStore = getMockStore({
        data: (
          state = {
            bookings: [],
            mediations: [],
            offers: [],
            stocks: [],
          }
        ) => state,
      })
      const wrapper = mount(
        <Provider store={mockStore}>
          <Router history={mockHistory}>
            <BookingActionContainer />
          </Router>
        </Provider>
      )

      // when
      wrapper.find({ children: 'J’y vais !' }).simulate('click')

      // then
      expect(`${mockHistory.location.pathname}${mockHistory.location.search}`).toBe(
        '/decouverte/reservation?param=value'
      )
    })
  })
})
