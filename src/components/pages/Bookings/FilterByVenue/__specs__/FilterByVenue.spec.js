import { shallow } from 'enzyme'
import FilterByVenue from '../FilterByVenue'
import React from 'react'

describe('src | components | pages | Bookings | FilterByVenue', () => {
  let props

  beforeEach(() => {
    props = {
      isDigital: false,
      loadVenues: jest.fn(),
      selectBookingsForVenues: jest.fn(),
      selectOnlyDigitalVenues: jest.fn(),
      venuesOptions: [{ name: 'Babar', id: 1 }, { name: 'Céleste', id: 2 }],
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<FilterByVenue {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
