import React from 'react'
import {shallow} from 'enzyme'
import Titles from '../../../layout/Titles/Titles'
import Bookings from '../Bookings.jsx'
import BookingsTable from "../BookingsTable/BookingsTable"

describe('src | components | pages | Bookings-v2', () => {
  let props

  beforeEach(() => {
    props = {
      requestGetAllBookingsRecap: jest.fn(),
    }
  })

  describe('the main section', () => {
    it('should render a Titles component and a BookingsTable component', () => {
      // given
      props.requestGetAllBookingsRecap = jest.fn()

      // when
      const wrapper = shallow(<Bookings {...props} />)

      // then
      const title = wrapper.find(Titles)
      const bookingsTable = wrapper.find(BookingsTable)
      expect(title).toHaveLength(1)
      expect(bookingsTable).toHaveLength(1)
    })
  })

  describe('handleSuccess', function () {
    it('should set bookingsRecap with api response data', function () {
      // Given
      props.requestGetAllBookingsRecap.mockReturnValue(
        new Promise(resolve => {
          resolve({
            payload: {
              data: [
                {
                  'offer-name': 'My Offer',
                },
              ],
            },
          })
        }),
      )

      // When
      const bookings = shallow(<Bookings {...props} />)
      console.log(bookings.state())

      // Then
      expect(bookings.state('bookingsRecap')).toBe([
        {
          'offer-name': 'My Offer',
        },
      ])
    })
  })
})
