import React from 'react'
import { shallow } from 'enzyme'
import Titles from '../../../layout/Titles/Titles'
import Bookings from '../Bookings.jsx'
import BookingsTable from '../BookingsTable/BookingsTable'

describe('src | components | pages | Bookings-v2', () => {
  let props

  beforeEach(() => {
    props = {
      requestGetAllBookingsRecap: jest.fn(),
    }
  })

  describe('the main section', () => {
    it('should render a Titles component and a BookingsTable component', () => {
      // When
      const wrapper = shallow(<Bookings {...props} />)

      // Then
      const title = wrapper.find(Titles)
      expect(title).toHaveLength(1)
      const bookingsTable = wrapper.find(BookingsTable)
      expect(bookingsTable).toHaveLength(1)
    })
  })

  describe('handleSuccess', function() {
    it('should set bookingsRecap with api response data', function() {
      // Given
      const state = {}
      const action = {
        payload: {
          data: [
            {
              'offer-name': 'My Offer',
            },
          ],
        },
      }
      jest
        .spyOn(props, 'requestGetAllBookingsRecap')
        .mockImplementation(handleSuccess => handleSuccess(state, action))

      // When
      const bookings = shallow(<Bookings {...props} />)

      // Then
      const bookingsTable = bookings.find(BookingsTable)
      expect(bookingsTable.prop('bookingsRecap')).toStrictEqual([
        {
          'offer-name': 'My Offer',
        },
      ])
    })
  })
})
