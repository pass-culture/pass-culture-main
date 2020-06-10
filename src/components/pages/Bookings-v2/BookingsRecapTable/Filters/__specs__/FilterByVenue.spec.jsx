import React from 'react'
import { shallow } from 'enzyme'
import FilterByVenue from '../FilterByVenue'

describe('components | FilterByVenue', () => {
  let props
  beforeEach(() => {
    props = {
      updateFilters: jest.fn(),
      selectedVenue: 'BG',
      venuesFormattedAndOrdered: [
        { id: 'AE', displayName: 'Ma premiere venue' },
        { id: 'BG', displayName: 'Ma seconde venue' },
      ],
    }
  })

  it('should render a select input containing venues options', async () => {
    // when
    const wrapper = await shallow(<FilterByVenue {...props} />)

    // then
    const venuesSelect = wrapper.find('select').at(0)
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions).toHaveLength(3)
    const venueTwo = venuesOptions.find({ children: 'Ma premiere venue' })
    expect(venueTwo).toHaveLength(1)
  })

  it('should apply offerVenue filter when selecting a venue', async () => {
    // given
    const selectedVenue = { target: { value: 'BG' } }
    const wrapper = await shallow(<FilterByVenue {...props} />)
    const venuesSelect = wrapper.find('select')

    // when
    await venuesSelect.simulate('change', selectedVenue)

    // then
    expect(props.updateFilters).toHaveBeenCalledWith({ offerVenue: 'BG' }, { selectedVenue: 'BG' })
  })

  it('should render a select input with a default value "Tous les lieux" selected', async () => {
    // given
    props.venuesFormattedAndOrdered = []

    // when
    const wrapper = await shallow(<FilterByVenue {...props} />)

    // then
    const venuesSelect = wrapper.find('select').at(0)
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions).toHaveLength(1)
    expect(venuesOptions.at(0).text()).toBe('Tous les lieux')
  })
})
