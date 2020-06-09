import React from 'react'
import Filters from '../Filters'
import { shallow } from 'enzyme'
import moment from 'moment'
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
      setFilters: jest.fn(),
    }
    fetchAllVenuesByProUser.mockResolvedValue([
      { id: 'AF', name: 'Librairie Fnac', offererName: 'gilbert Joseph', isVirtual: false },
      { id: 'AE', name: 'Offre numérique', offererName: 'gilbert Joseph', isVirtual: true },
    ])
  })

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  it('should apply offerName filter when typing keywords', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const instance = wrapper.instance()
    instance.handleOmniSearchCriteriaChange({ target: { value: 'offre' } })

    // When
    instance.handleOmniSearchChange({ target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: '',
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerName: 'Jurassic Park',
      offerDate: null,
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply offerDate filter when choosing an offer date', () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)

    // When
    wrapper.instance().handleOfferDateChange(selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingBeneficiary: '',
      bookingEndingDate: null,
      offerDate: '2020-05-20',
      offerName: '',
      offerVenue: ALL_VENUES,
    })
  })

  it('should add filter to previous filters when applying a new one', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const selectedDate = moment('2020-05-20')
    const wrapperInstance = wrapper.instance()
    wrapperInstance.handleOfferDateChange(selectedDate)

    // When
    wrapperInstance.handleOfferNameChange('Jurassic Park')

    // Then
    expect(props.setFilters).toHaveBeenCalledTimes(2)
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: '',
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerDate: '2020-05-20',
      offerName: 'Jurassic Park',
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply bookingBeginningDate filter when choosing an booking beginning date', () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)

    // When
    wrapper.instance().handleBookingBeginningDateChange(selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: '',
      bookingBeginningDate: '2020-05-20',
      bookingEndingDate: null,
      offerDate: null,
      offerName: '',
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply bookingEndingDate filter when choosing an booking end date', () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)

    // When
    wrapper.instance().handleBookingEndingDateChange(selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: '',
      bookingBeginningDate: null,
      bookingEndingDate: '2020-05-20',
      offerDate: null,
      offerName: '',
      offerVenue: ALL_VENUES,
    })
  })

  it('should apply offerVenue filter when selecting a venue', () => {
    // given
    const wrapper = shallow(<Filters {...props} />)
    wrapper.instance()['venueSelect'] = {
      current: {
        blur: jest.fn(),
      },
    }

    // when
    wrapper.instance().handleVenueSelection({ target: { value: 'AE' } })

    // then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: '',
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerDate: null,
      offerName: '',
      offerVenue: 'AE',
    })
  })

  it('should apply bookingBeneficiary filter when typing keywords for beneficiary name or email', () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const instance = wrapper.instance()
    instance.handleOmniSearchCriteriaChange({ target: { value: 'bénéficiaire' } })

    // When
    instance.handleOmniSearchChange({ target: { value: 'Firost' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeneficiary: 'Firost',
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerName: '',
      offerDate: null,
      offerVenue: 'all',
    })
  })

  it('should fetch venues of pro user when mounting component', () => {
    // when
    shallow(<Filters {...props} />)

    // then
    expect(fetchAllVenuesByProUser).toHaveBeenCalledTimes(1)
  })
})
