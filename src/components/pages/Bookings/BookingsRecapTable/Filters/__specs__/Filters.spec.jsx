import React from 'react'
import Filters from '../Filters'
import { ALL_VENUES, EMPTY_FILTER_VALUE } from '../_constants'
import { mount, shallow } from 'enzyme'
import { fetchAllVenuesByProUser } from '../../../../../../services/venuesService'
import FilterByOmniSearch from '../FilterByOmniSearch'
import FilterByEventDate from '../FilterByEventDate'
import FilterByVenue from '../FilterByVenue'
import FilterByBookingPeriod from '../FilterByBookingPeriod'

jest.mock('../../../../../../services/venuesService', () => ({
  fetchAllVenuesByProUser: jest.fn(),
}))
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
describe('components | Filters', () => {
  let props

  beforeEach(() => {
    props = {
      isLoading: false,
      oldestBookingDate: EMPTY_FILTER_VALUE,
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

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  it('should render all filters component with expected props', async () => {
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
    const filterByEventDate = wrapper.find(FilterByEventDate)
    expect(filterByEventDate.props()).toStrictEqual({
      isDisabled: false,
      selectedOfferDate: '',
      updateFilters: expect.any(Function),
    })
    const filterByVenue = wrapper.find(FilterByVenue)
    expect(filterByVenue.props()).toStrictEqual({
      isDisabled: false,
      selectedVenue: '',
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
      isDisabled: false,
      oldestBookingDate: '',
      selectedBookingBeginningDate: '',
      selectedBookingEndingDate: expect.any(Object),
      updateFilters: expect.any(Function),
    })
  })

  it('should apply offerName filter when typing keywords', async () => {
    // Given
    const wrapper = mount(<Filters {...props} />)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerName: 'Jurassic Park',
      offerISBN: EMPTY_FILTER_VALUE,
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply given filter', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const updatedFilter = { offerDate: '2020-05-20' }

    // When
    wrapper.instance().updateFilters(updatedFilter)

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: '2020-05-20',
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply default filters when mounting component', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    // When
    wrapper.instance().updateFilters()

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: ALL_VENUES,
    })
  })

  it('should add filter to previous filters when applying a new one', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const wrapperInstance = wrapper.instance()
    const firstUpdatedFilter = { offerDate: '2020-05-20' }
    wrapperInstance.updateFilters(firstUpdatedFilter)
    const secondUpdatedFilter = { offerVenue: 'AE' }

    // When
    wrapperInstance.updateFilters(secondUpdatedFilter)

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledTimes(2)
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: '2020-05-20',
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: 'AE',
    })
  })

  it('should add all filters when applying new ones', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const wrapperInstance = wrapper.instance()
    const firstUpdatedFilter = { bookingBeneficiary: 'riri' }
    wrapperInstance.updateFilters(firstUpdatedFilter)
    const someUpdatedFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: '12457',
      offerName: EMPTY_FILTER_VALUE,
    }

    // When
    wrapperInstance.updateFilters(someUpdatedFilters)

    // Then
    expect(props.updateGlobalFilters).toHaveBeenCalledTimes(2)
    expect(props.updateGlobalFilters).toHaveBeenCalledWith({
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingBeginningDate: EMPTY_FILTER_VALUE,
      bookingEndingDate: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerDate: EMPTY_FILTER_VALUE,
      offerISBN: '12457',
      offerName: EMPTY_FILTER_VALUE,
      offerVenue: ALL_VENUES,
    })
  })

  it('should fetch venues of pro user when mounting component', () => {
    // when
    shallow(<Filters {...props} />)

    // then
    expect(fetchAllVenuesByProUser).toHaveBeenCalledTimes(1)
  })
})
