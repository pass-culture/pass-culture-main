import { shallow } from 'enzyme'
import React from 'react'
import { SearchCriteria } from '../SearchCriteria'
import { CATEGORY_CRITERIA } from '../searchCriteriaValues'

describe('src | components | pages | search-algolia | Criteria | SearchCriteria', () => {
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
      <SearchCriteria
        {...props}
        activeCriterionLabel="Toutes les catégories"
        criteria={CATEGORY_CRITERIA}
        onCriterionSelection={onCriterionSelection}
        title="Catégories"
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
})
