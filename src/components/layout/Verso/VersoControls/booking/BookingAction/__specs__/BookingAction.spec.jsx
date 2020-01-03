import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import BookingAction from '../BookingAction'
import BookingActionContainer from '../BookingActionContainer'
import getMockStore from '../../../../../../../utils/mockStore'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

describe('src | components | layout | Verso | VersoControls | booking | BookingAction | BookingAction', () => {
  let props

  beforeEach(() => {
    props = {
      history: {
        push: jest.fn(),
      },
      bookingUrl: 'http://booking-layout.com',
      priceRange: [10, 30],
    }
  })

  describe('when the offer is bookable', () => {
    it('should render a price and label within link', () => {
      // given
      props.isNotBookable = false

      // when
      const wrapper = shallow(<BookingAction {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the offer is not bookable', () => {
    it('should render a price and label within a wrapper', () => {
      // given
      props.isNotBookable = true

      // when
      const wrapper = shallow(<BookingAction {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
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
