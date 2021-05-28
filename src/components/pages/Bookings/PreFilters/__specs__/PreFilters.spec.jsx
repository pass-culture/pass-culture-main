import { mount } from 'enzyme'
import React from 'react'

import { fetchAllVenuesByProUser } from 'repository/venuesService'

import { ALL_VENUES } from '../_constants'
import FilterByBookingPeriod from '../FilterByBookingPeriod'
import FilterByEventDate from '../FilterByEventDate'
import FilterByVenue from '../FilterByVenue'
import PreFilters from '../PreFilters'

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
  fetchAllVenuesByProUser: jest.fn(),
}))
describe('components | PreFilters', () => {
  let props

  beforeEach(() => {
    props = {
      isLoading: false,
      updateGlobalFilters: jest.fn(),
      offerVenue: ALL_VENUES,
    }
    fetchAllVenuesByProUser.mockResolvedValue([
      {
        id: 'AF',
        name: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: false,
      },
      {
        id: 'AE',
        name: 'Offre numérique',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      },
    ])
  })

  it('should render all filters component with expected props', async () => {
    // when
    const wrapper = await mount(<PreFilters {...props} />)

    // then
    const filterByEventDate = wrapper.find(FilterByEventDate)
    expect(filterByEventDate.props()).toStrictEqual({
      selectedOfferDate: '',
      updateFilters: expect.any(Function),
    })
    const filterByVenue = wrapper.find(FilterByVenue)
    expect(filterByVenue.props()).toStrictEqual({
      selectedVenue: ALL_VENUES,
      updateFilters: expect.any(Function),
      venuesFormattedAndOrdered: [
        {
          displayName: 'gilbert Joseph - Offre numérique',
          id: 'AE',
        },
        {
          displayName: 'Librairie Fnac',
          id: 'AF',
        },
      ],
    })
    const filterByBookingPeriod = wrapper.find(FilterByBookingPeriod)
    expect(filterByBookingPeriod.props()).toStrictEqual({
      selectedBookingBeginningDate: '',
      selectedBookingEndingDate: expect.any(Object),
      updateFilters: expect.any(Function),
    })
  })

  it('should fetch venues of pro user when mounting component', () => {
    // when
    mount(<PreFilters {...props} />)

    // then
    expect(fetchAllVenuesByProUser).toHaveBeenCalledTimes(1)
  })
})
