import { shallow } from 'enzyme'
import React from 'react'
import Header from '../../../../layout/Header/Header'
import { Criteria } from '../Criteria'
import { CATEGORY_CRITERIA } from '../criteriaEnums'

describe('components | Criteria', () => {
  let props
  beforeEach(() => {
    props = {
      activeCriterionLabel: 'Toutes les catégories',
      backTo: '/recherche-offres',
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

  it('should render a Header component with the right props', () => {
    // When
    const wrapper = shallow(<Criteria {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toStrictEqual('/recherche-offres')
    expect(header.prop('closeTo')).toStrictEqual(null)
    expect(header.prop('history')).toStrictEqual(props.history)
    expect(header.prop('location')).toStrictEqual(props.history.location)
    expect(header.prop('match')).toStrictEqual(props.match)
    expect(header.prop('title')).toStrictEqual(props.title)
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
