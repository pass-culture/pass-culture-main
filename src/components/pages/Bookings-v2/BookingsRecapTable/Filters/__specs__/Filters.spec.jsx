import React from 'react'
import Filters from '../Filters'
import { mount, shallow } from 'enzyme'
import moment from 'moment'
import { fetchAllVenuesByProUser } from '../../../../../../services/venuesService'

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
      { id: 'AF', name: 'Librairie Fnac', offererName: 'Gilbert Joseph', isVirtual: false },
      { id: 'AE', name: 'Offre numérique', offererName: 'Gilbert Joseph', isVirtual: true },
    ])
  })

  afterEach(() => {
    fetchAllVenuesByProUser.mockReset()
  })

  it('should apply offerName filter when typing keywords', async () => {
    // Given
    const wrapper = shallow(<Filters {...props} />)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerName: 'Jurassic Park',
      offerDate: null,
      offerVenue: '',
    })
  })

  it('should apply offerDate filter when choosing an offer date', async () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(0)

    // When
    await offerDateInput.simulate('change', selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerDate: '2020-05-20',
      offerName: null,
      offerVenue: '',
    })
  })

  it('should add filter to previous filters when applying a new one', async () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(0)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })
    await offerDateInput.simulate('change', selectedDate)

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledTimes(2)
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerDate: '2020-05-20',
      offerName: 'Jurassic Park',
      offerVenue: '',
    })
  })

  it('should apply bookingBeginningDate filter when choosing an booking beginning date', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(1)

    // When
    await offerDateInput.simulate('change', selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: '2020-05-20',
      bookingEndingDate: null,
      offerDate: null,
      offerName: null,
      offerVenue: '',
    })
  })

  it('should apply bookingEndingDate filter when choosing an booking end date', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(2)

    // When
    await offerDateInput.simulate('change', selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingEndingDate: '2020-05-20',
      offerDate: null,
      offerName: null,
      offerVenue: '',
    })
  })

  it('should fetch venues of pro user when mounting component', async () => {
    // when
    shallow(<Filters {...props} />)

    // then
    expect(fetchAllVenuesByProUser).toHaveBeenCalledTimes(1)
  })

  it('should render a select input with a default value "Tous les lieux" selected', async () => {
    // given
    fetchAllVenuesByProUser.mockResolvedValue([])

    // when
    const wrapper = await shallow(<Filters {...props} />)

    // then
    const venuesSelect = wrapper.find('select')
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions).toHaveLength(1)
    expect(venuesOptions.at(0).text()).toBe('Tous les lieux')
  })

  it('should render a select input containing venues options', async () => {
    // when
    const wrapper = await shallow(<Filters {...props} />)

    // then
    const venuesSelect = wrapper.find('select')
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions).toHaveLength(3)
    const venueTwo = venuesOptions.find({ children: 'Librairie Fnac' })
    expect(venueTwo).toHaveLength(1)
  })

  it('should show venue option with "offerer name - offre numérique" when venue is virtual', async () => {
    // when
    const wrapper = await shallow(<Filters {...props} />)

    // then
    const venuesSelect = wrapper.find('select')
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions).toHaveLength(3)
    const venueOne = venuesOptions.find({ children: 'Gilbert Joseph - Offre numérique' })
    expect(venueOne).toHaveLength(1)
  })

  it('should show order venue option alphabetically', async () => {
    // when
    const wrapper = await shallow(<Filters {...props} />)

    // then
    const venuesSelect = wrapper.find('select')
    const venuesOptions = venuesSelect.find('option')
    expect(venuesOptions.at(1).text()).toBe('Gilbert Joseph - Offre numérique')
    expect(venuesOptions.at(2).text()).toBe('Librairie Fnac')
  })

  it('should apply offerVenue filter when selecting a venue', async () => {
    // given
    const wrapper = await mount(<Filters {...props} />)
    const venuesSelect = wrapper.find('select')

    // when
    await venuesSelect.simulate('change', { target: { value: 'AE' } })

    // then
    expect(props.setFilters).toHaveBeenCalledWith({
      bookingBeginningDate: null,
      bookingEndingDate: null,
      offerDate: null,
      offerName: null,
      offerVenue: 'AE',
    })
  })

  it('should not allow to select booking beginning date superior to booking ending date value', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const bookingEndingDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(2)
    await bookingEndingDateInput.simulate('change', selectedDate)

    // When
    const bookingBeginningDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(1)

    // Then
    expect(bookingBeginningDateInput.prop('maxDate')).toStrictEqual(selectedDate)
  })

  it('should not allow to select booking ending date inferior to booking beginning date value', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const bookingBeginningDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(1)
    await bookingBeginningDateInput.simulate('change', selectedDate)

    // When
    const bookingEndingDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(2)

    // Then
    expect(bookingEndingDateInput.prop('minDate')).toStrictEqual(selectedDate)
  })
})
