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
      isQrCodeFeatureDisabled: false,
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

      // then
      const loader = wrapper.find(LoaderContainer)
      expect(loader).toHaveLength(1)
    })
  })

  describe('navigating on routes', () => {
    let history

    beforeEach(() => {
      props.requestGetBookings.mockImplementation((fail, success) => success())
      history = createMemoryHistory()
    })

    it('should render a list of my bookings when navigating on my bookings page', () => {
      // given
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

    it('should render a qr code when navigating on qr code page and qr code feature is active', () => {
      // given
      props.isQrCodeFeatureDisabled = false
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

    it('should not render a qr code when navigating on qr code page and qr code feature is not active', () => {
      // given
      props.isQrCodeFeatureDisabled = true
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
      expect(qrCode).toHaveLength(0)
    })
  })
})
