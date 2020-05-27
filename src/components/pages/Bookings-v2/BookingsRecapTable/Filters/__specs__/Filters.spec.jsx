import React from 'react'
import Filters from '../Filters'
import { shallow } from 'enzyme'
import moment from 'moment'

jest.mock('lodash.debounce', () => jest.fn(callback => callback))

describe('components | Filters', () => {
  it('should apply offerName filter when typing keywords', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const wrapper = shallow(<Filters {...props} />)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({ offerName: 'Jurassic Park', offerDate: null })
  })

  it('should apply offerDate filter when choosing an offer Data', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' })

    // When
    await offerDateInput.simulate('change', selectedDate)

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({ offerName: null, offerDate: '2020-05-20' })
  })

  it('should add filter to previous filters when applying a new one', async () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<Filters {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' })
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })
    await offerDateInput.simulate('change', selectedDate)

    // When
    await offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledTimes(2)
    expect(props.setFilters).toHaveBeenCalledWith({
      offerName: 'Jurassic Park',
      offerDate: '2020-05-20',
    })
  })
})
