import { mount, shallow } from 'enzyme'
import React from 'react'

import MyBookings from '../MyBookings'
import { Router } from 'react-router-dom'
import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import QrCodeContainer from '../MyBookingsLists/BookingsList/QrCode/QrCodeContainer'
import { createMemoryHistory } from 'history'
import MyBookingsListsContainer from '../MyBookingsLists/MyBookingsListsContainer'
import { Provider } from 'react-redux'
import state from '../../../../mocks/state'
import MyBookingDetailsContainer from '../MyBookingDetails/MyBookingDetailsContainer'
import configureStore from 'redux-mock-store'
import thunk from 'redux-thunk'

describe('src | components | pages | my-bookings | MyBookings', () => {
  let props
  let store
  const buildStore = configureStore([thunk])

  beforeEach(() => {
    props = {
      bookings: [],
      location: {
        pathname: '/reservations',
        search: '',
      },
      match: {
        params: {},
      },
      requestGetBookings: jest.fn(),
    }
    store = buildStore(state)
  })

  describe('render', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('should render a LoaderContainer component when mounted', () => {
      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then¬
      const loader = wrapper.find(LoaderContainer)
      expect(loader).toHaveLength(1)
    })
  })

  describe('navigating on routes', () => {
    beforeEach(() => {
      props.requestGetBookings.mockImplementation((fail, success) => success())
    })

    it('should render a MyBookingsListsContainer component when navigating on "/reservations" path', () => {
      // given
      const history = createMemoryHistory()
      history.push('/reservations')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <MyBookings {...props} />
          </Provider>
        </Router>
      )

      // then
      const myBookings = wrapper.find(MyBookingsListsContainer)
      const myBooking = wrapper.find(MyBookingDetailsContainer)
      const qrCode = wrapper.find(QrCodeContainer)
      expect(myBookings).toHaveLength(1)
      expect(myBooking).toHaveLength(0)
      expect(qrCode).toHaveLength(0)
    })

    it('should render a QrCodeContainer component when navigating on "/reservations/details/AE/qrcode" path', () => {
      const history = createMemoryHistory()
      history.push('/reservations/details/A9/qrcode')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <MyBookings {...props} />
          </Provider>
        </Router>
      )

      // then
      const myBookings = wrapper.find(MyBookingsListsContainer)
      const myBooking = wrapper.find(MyBookingDetailsContainer)
      const qrCode = wrapper.find(QrCodeContainer)
      expect(myBookings).toHaveLength(0)
      expect(myBooking).toHaveLength(0)
      expect(qrCode).toHaveLength(1)
    })
  })
})
