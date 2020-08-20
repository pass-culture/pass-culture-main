import { mount, shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyBookingDetailsContainer from '../MyBookingDetails/MyBookingDetailsContainer'
import MyBookings from '../MyBookings'
import QrCodeContainer from '../MyBookingsLists/BookingsList/QrCode/QrCodeContainer'
import MyBookingsListsContainer from '../MyBookingsLists/MyBookingsListsContainer'
import getMockStore from '../../../../utils/mockStore'

describe('src | components | MyBookings', () => {
  let props
  let mockStore

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
        path: '/reservations',
      },
      requestGetBookings: jest.fn(),
    }
    mockStore = getMockStore({
      data: (
        state = {
          bookings: [
            {
              id: 'A9',
              stockId: 's1',
              token: 't',
            },
          ],
          features: [],
          offers: [
            {
              id: 'o1',
              name: 'fake offer',
              venue: {
                departementCode: '',
                name: 'fake venue',
              },
            },
          ],
          stocks: [
            {
              id: 's1',
              offerId: 'o1',
              beginningDatetime: '2019-07-08T20:00:00Z',
            },
          ],
        }
      ) => state,
    })
  })

  describe('render', () => {
    it('should render a LoaderContainer component when mounted', () => {
      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then
      const loader = wrapper.find(LoaderContainer)
      expect(loader).toHaveLength(1)
    })
  })

  describe('navigating on routes', () => {
    beforeEach(() => {
      props.requestGetBookings.mockImplementation((fail, success) => success())
    })

    it('should render a list of my bookings when navigating on my bookings page', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={[props.match.path]}>
          <Provider store={mockStore}>
            <MyBookings {...props} />
          </Provider>
        </MemoryRouter>
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

      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={[`${props.match.path}/details/A9/qrcode`]}>
          <Provider store={mockStore}>
            <MyBookings {...props} />
          </Provider>
        </MemoryRouter>
      )

      // then
      const myBookings = wrapper.find(MyBookingsListsContainer)
      const myBooking = wrapper.find(MyBookingDetailsContainer)
      const qrCode = wrapper.find(QrCodeContainer)
      expect(myBookings).toHaveLength(1)
      expect(myBooking).toHaveLength(0)
      expect(qrCode).toHaveLength(1)
    })

    it('should not render a qr code when navigating on qr code page and qr code feature is not active', () => {
      // given
      props.isQrCodeFeatureDisabled = true

      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={[`${props.match.path}/details/A9/qrcode`]}>
          <Provider store={mockStore}>
            <MyBookings {...props} />
          </Provider>
        </MemoryRouter>
      )

      // then
      const myBookings = wrapper.find(MyBookingsListsContainer)
      const myBooking = wrapper.find(MyBookingDetailsContainer)
      const qrCode = wrapper.find(QrCodeContainer)
      expect(myBookings).toHaveLength(1)
      expect(myBooking).toHaveLength(0)
      expect(qrCode).toHaveLength(0)
    })
  })
})
