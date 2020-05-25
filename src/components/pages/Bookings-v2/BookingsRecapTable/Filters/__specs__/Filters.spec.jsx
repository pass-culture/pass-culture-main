import React from 'react'
import Filters from '../Filters'
import { shallow } from 'enzyme'

jest.mock('lodash.debounce', () => jest.fn(callback => callback))

describe('components | Filters', () => {
  it('should apply offerName filter when typing keywords', () => {
    // Given
    const props = {
      setFilters: jest.fn(),
    }
    const wrapper = shallow(<Filters {...props} />)
    const offerNameInput = wrapper.find({ placeholder: "Rechercher par nom d'offre" })

    // When
    offerNameInput.simulate('change', { target: { value: 'Jurassic Park' } })

    // Then
    expect(props.setFilters).toHaveBeenCalledWith({ offerName: 'Jurassic Park' })
  })
})
