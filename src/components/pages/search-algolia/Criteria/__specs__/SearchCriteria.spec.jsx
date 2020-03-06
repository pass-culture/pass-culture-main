import { shallow } from 'enzyme'
import React from 'react'
import Header from '../../../../layout/Header/Header'
import { SearchCriteria } from '../SearchCriteria'
import { CATEGORY_CRITERIA } from '../searchCriteriaValues'

describe('components | SearchCriteria', () => {
  let props
  beforeEach(() => {
    props = {
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
      activeCriterionLabel: 'Toutes les catégories',
      criteria: CATEGORY_CRITERIA,
      onCriterionSelection: jest.fn(),
      title: 'Catégories',
    }
  })
  it('should render a Header component with the right props', () => {
    // When
    const wrapper = shallow(<SearchCriteria {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toStrictEqual('/recherche-offres')
    expect(header.prop('closeTo')).toStrictEqual('')
    expect(header.prop('history')).toStrictEqual(props.history)
    expect(header.prop('location')).toStrictEqual(props.history.location)
    expect(header.prop('match')).toStrictEqual(props.match)
    expect(header.prop('title')).toStrictEqual(props.title)
  })

  it('should set category filter for search when "Cinéma" is selected', () => {
    // Given
    const wrapper = shallow(<SearchCriteria {...props} />)
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
