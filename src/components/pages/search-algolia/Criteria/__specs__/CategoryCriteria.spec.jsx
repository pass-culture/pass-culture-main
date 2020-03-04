import { shallow } from 'enzyme'
import React from 'react'
import CategoryCriteria from '../CategoryCriteria'

describe('src | components | pages | search-algolia | Criteria | CategoryCriteria', () => {
  let props
  beforeEach(() => {
    props = {
      history: {
        push: () => {},
        replace: () => {},
      },
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
    }
  })

  it('should set category filter for search when "Cinéma" is selected', () => {
    // Given
    const onCriterionSelection = jest.fn()
    const wrapper = shallow(
      <CategoryCriteria
        {...props}
        activeCriterionLabel="Toutes les catégories"
        onCriterionSelection={onCriterionSelection}
      />
    )
    const cinemaCategory = wrapper.find({
      children: 'Cinéma',
    })
    const cinemaCategoryButton = cinemaCategory.parent()

    // When
    cinemaCategoryButton.simulate('click')

    // Then
    expect(onCriterionSelection).toHaveBeenCalledWith('CINEMA')
  })

  it('should not set category filter for search when "Toutes les catégories" is selected', () => {
    // Given
    const onCriterionSelection = jest.fn()
    const wrapper = shallow(
      <CategoryCriteria
        {...props}
        activeCriterionLabel="Toutes les catégories"
        onCriterionSelection={onCriterionSelection}
      />
    )
    const allCategories = wrapper.find({
      children: 'Toutes les catégories',
    })
    const allCategoriesButton = allCategories.parent()

    // When
    allCategoriesButton.simulate('click')

    // Then
    expect(onCriterionSelection).toHaveBeenCalledWith('ALL')
  })
})
