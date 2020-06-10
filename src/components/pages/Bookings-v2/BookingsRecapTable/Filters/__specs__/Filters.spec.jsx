import React from 'react'
import Filters, { EMPTY_FILTER_VALUE } from '../Filters'
import { mount, shallow } from 'enzyme'
import { fetchAllVenuesByProUser } from '../../../../../../services/venuesService'
import { ALL_VENUES } from '../../utils/filterBookingsRecap'

jest.mock('../../../../../../services/venuesService', () => ({
  fetchAllVenuesByProUser: jest.fn(),
}))
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
describe('components | Filters', () => {
  let props

  beforeEach(() => {
    props = {
      oldestBookingDate: EMPTY_FILTER_VALUE,
      setFilters: jest.fn(),
    }
    fetchAllVenuesByProUser.mockResolvedValue([
      {
        id: 'AF',
        booking_token: 'TOLKIEN',
        name: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: false,
      },
      {
        id: 'AE',
        booking_token: 'NEIKLOT',
        name: 'Offre numérique',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      },
    ])
  })

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  it('should apply offerName filter when typing keywords', async () => {
    // Given
    const wrapper = mount(<Filters {...props} />)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
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
    expect(props.setFilters).toHaveBeenCalledWith({
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
    expect(props.setFilters).toHaveBeenCalledTimes(2)
    expect(props.setFilters).toHaveBeenCalledWith({
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
    expect(props.setFilters).toHaveBeenCalledTimes(2)
    expect(props.setFilters).toHaveBeenCalledWith({
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
