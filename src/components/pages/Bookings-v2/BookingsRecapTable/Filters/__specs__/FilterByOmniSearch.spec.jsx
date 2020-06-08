import FilterByOmniSearch from '../FilterByOmniSearch'
import React from 'react'
import { shallow } from 'enzyme'

describe('components | FilterByOmniSearch', () => {
  let props
  beforeEach(() => {
    props = {
      omniSearchSelectOptions: [
        {
          id: 'AA',
          selectOptionText: 'First Select',
        },
        {
          id: 'BB',
          selectOptionText: 'Second Select',
        },
      ],
      handleOmniSearchCriteriaChange: jest.fn(),
      handleOmniSearchChange: jest.fn(),
      placeholderText: 'Mon petit placeholder',
      keywords: 'mesKeywords',
    }
  })

  it('should display a select input with the given options', () => {
    // When
    const wrapper = shallow(<FilterByOmniSearch {...props} />)
    const select = wrapper.find('select')
    const options = select.find('option')

    // Then
    expect(select).toHaveLength(1)
    expect(options).toHaveLength(2)
    expect(options.at(0).text()).toStrictEqual('First Select')
    expect(options.at(0).props()).toStrictEqual({ children: 'First Select', value: 'AA' })
    expect(options.at(1).text()).toStrictEqual('Second Select')
    expect(options.at(1).props()).toStrictEqual({ children: 'Second Select', value: 'BB' })
  })

  it('should display the correct placeholder for current option selected', () => {
    // When
    const wrapper = shallow(<FilterByOmniSearch {...props} />)
    const input = wrapper.find('input')

    // Then
    expect(input.prop('placeholder')).toStrictEqual('Mon petit placeholder')
    expect(input.prop('value')).toStrictEqual('mesKeywords')
  })
})
