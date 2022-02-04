import { mount, shallow } from 'enzyme'
import React from 'react'

import { fetchAllVenuesByProUser } from 'repository/venuesService'

import { EMPTY_FILTER_VALUE } from '../_constants'
import FilterByOmniSearch from '../FilterByOmniSearch'
import Filters from '../Filters'

jest.mock('repository/venuesService', () => ({
  ...jest.requireActual('repository/venuesService'),
  fetchAllVenuesByProUser: jest.fn(),
}))
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
describe('components | Filters', () => {
  let props

  beforeEach(() => {
    props = {
      isLoading: false,
      updateGlobalFilters: jest.fn(),
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

  it('should render omnisearch component with expected props', async () => {
    // when
    const wrapper = await shallow(<Filters {...props} />)

    // then
    const filterByOmniSearch = wrapper.find(FilterByOmniSearch)
    expect(filterByOmniSearch.props()).toStrictEqual({
      isDisabled: false,
      keywords: '',
      selectedOmniSearchCriteria: 'offre',
      updateFilters: expect.any(Function),
    })
  })

  it('should apply offerName filter when typing keywords', async () => {
    // Given
    const wrapper = mount(<Filters {...props} />)
    const offerNameInput = wrapper.find({
      placeholder: "Rechercher par nom d'offre",
    })

    // When
    await offerNameInput.simulate('change', {
      target: { value: 'Jurassic Park' },
    })

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerName: 'Jurassic Park',
      offerISBN: EMPTY_FILTER_VALUE,
    })
  })

  it('should apply default filters when mounting component', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    // When
    wrapper.instance().updateFilters()

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    })
  })
})
