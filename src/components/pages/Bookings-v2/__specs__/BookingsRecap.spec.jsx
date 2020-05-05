import React from 'react'
import { shallow } from 'enzyme'
import Titles from '../../../layout/Titles/Titles'
import BookingsRecap from '../BookingsRecap'
import BookingsRecapTable from '../BookingsRecapTable/BookingsRecapTable'

describe('src | components | pages | Bookings-v2', () => {
  let props

  beforeEach(() => {
    props = {
      requestGetAllBookingsRecap: jest.fn(),
    }
  })

  describe('the main section', () => {
    it('should render a Titles component and a BookingsRecapTable component', () => {
      // When
      const wrapper = shallow(<BookingsRecap {...props} />)

      // Then
      const title = wrapper.find(Titles)
      expect(title).toHaveLength(1)
      const bookingsTable = wrapper.find(BookingsRecapTable)
      expect(bookingsTable).toHaveLength(1)
    })
  })

  describe('handleSuccess', () => {
    it('should set bookingsRecap with api response data', () => {
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
      const bookings = shallow(<BookingsRecap {...props} />)

      // Then
      const bookingsTable = bookings.find(BookingsRecapTable)
      expect(bookingsTable.prop('bookingsRecap')).toStrictEqual([
        {
          'offer-name': 'My Offer',
        },
      ])
    })
  })
})
