import { shallow } from 'enzyme'
import React from 'react'

import FilterByOmniSearch from '../FilterByOmniSearch'

describe('components | FilterByOmniSearch', () => {
  let props
  beforeEach(() => {
    props = {
      keywords: '',
      selectedOmniSearchCriteria: 'offre',
      updateFilters: jest.fn(),
    }
  })

  it('should display a select input with the given options', () => {
    // When
    const wrapper = shallow(<FilterByOmniSearch {...props} />)
    const select = wrapper.find('select')
    const options = select.find('option')

    // Then
    expect(select).toHaveLength(1)
    expect(options).toHaveLength(4)
    expect(options.at(0).text()).toBe('Offre')
    expect(options.at(0).prop('value')).toBe('offre')
    expect(options.at(1).text()).toBe('Bénéficiaire')
    expect(options.at(1).prop('value')).toBe('bénéficiaire')
    expect(options.at(2).text()).toBe('ISBN')
    expect(options.at(2).prop('value')).toBe('isbn')
    expect(options.at(3).text()).toBe('Contremarque')
    expect(options.at(3).prop('value')).toBe('contremarque')
  })

  it('should display the correct placeholder for current option selected', () => {
    // When
    const wrapper = shallow(<FilterByOmniSearch {...props} />)
    const input = wrapper.find('input')

    // Then
    expect(input.prop('placeholder')).toBe("Rechercher par nom d'offre")
  })

  it('should apply bookingBeneficiary filter when typing keywords for beneficiary name or email', async () => {
    // Given
    props.selectedOmniSearchCriteria = 'bénéficiaire'
    const wrapper = shallow(<FilterByOmniSearch {...props} />)
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Firost' } })

    // Then
    expect(props.updateFilters).toHaveBeenCalledWith(
      {
        bookingBeneficiary: 'Firost',
        bookingToken: '',
        offerISBN: '',
        offerName: '',
      },
      { keywords: 'Firost', selectedOmniSearchCriteria: 'bénéficiaire' }
    )
  })

  it('should update the selected omniSearch criteria when selecting an omniSearchCriteria', async () => {
    // Given
    props.keywords = '12548'
    let wrapper = await shallow(<FilterByOmniSearch {...props} />)
    const omniSearchSelect = wrapper.find('select')

    // When
    await omniSearchSelect.simulate('change', { target: { value: 'isbn' } })

    // Then
    expect(props.updateFilters).toHaveBeenCalledWith(
      {
        bookingBeneficiary: '',
        bookingToken: '',
        offerISBN: '12548',
        offerName: '',
      },
      { keywords: '12548', selectedOmniSearchCriteria: 'isbn' }
    )
  })
})
