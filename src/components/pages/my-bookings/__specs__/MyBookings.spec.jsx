import { shallow } from 'enzyme'
import React from 'react'

import MyBookings from '../MyBookings'

describe('src | components | pages | my-bookings | MyBookings', () => {
  let props

  beforeEach(() => {
    props = {
      bookings: [
        {
          id: 'b1',
        },
      ],
      location: {
        pathname: '/reservations',
        search: '',
      },
      match: {
        params: {},
      },
    }
  })

  describe('when there is something wrong with API', () => {
    it('should display a loader', () => {
      // given
      props.requestGetBookings = () => []

      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the API response good data', () => {
    it('should display my bookings', () => {
      // given
      props.requestGetBookings = (handleFail, handleSuccess) => {
        handleSuccess()
        return [
          {
            id: 'b1',
          },
        ]
      }

      // when
      const wrapper = shallow(<MyBookings {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
