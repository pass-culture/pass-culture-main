import { shallow } from 'enzyme'
import React from 'react'
import { Criteria } from '../Criteria'
import { CATEGORY_CRITERIA } from '../criteriaEnums'

describe('components | Criteria', () => {
  let props
  beforeEach(() => {
    props = {
      activeCriterionLabel: 'Toutes les catégories',
      backTo: '/recherche',
      criteria: CATEGORY_CRITERIA,
      history: {
        push: () => {},
        replace: () => {},
        location: {
          pathname: '',
          search: '',
        },
      },
      match: {
        params: {},
      },
      onCriterionSelection: jest.fn(),
      title: 'Catégories',
    }
  })

  it('should set category filter for search when "Cinéma" is selected', () => {
    // Given
    const wrapper = shallow(<Criteria {...props} />)
    const cinemaCategory = wrapper.find({
      children: 'Cinéma',
    })
    const cinemaCategoryButton = cinemaCategory.parent()

    // When
    cinemaCategoryButton.simulate('click')

    // Then
    expect(props.onCriterionSelection).toHaveBeenCalledWith('CINEMA')
  })
})
