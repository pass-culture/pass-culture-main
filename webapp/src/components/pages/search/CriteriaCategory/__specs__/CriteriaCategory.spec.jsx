import { shallow } from 'enzyme'
import React from 'react'
import Header from '../../../../layout/Header/Header'
import { CATEGORY_CRITERIA } from '../../Criteria/criteriaEnums'
import { Criteria } from '../../Criteria/Criteria'
import CriteriaCategory from '../CriteriaCategory'

describe('components | CriteriaCategory', () => {
  let props
  beforeEach(() => {
    props = {
      activeCriterionLabel: 'Toutes les catégories',
      backTo: '/recherche',
      criteria: CATEGORY_CRITERIA,
      history: {
        location: {
          pathname: '',
          search: '',
        },
        push: () => {},
        replace: () => {},
      },
      match: {
        params: {},
      },
      onCriterionSelection: jest.fn(),
      title: 'Catégories',
    }
  })

  it('should render a Header component with the right props', () => {
    // when
    const wrapper = shallow(<CriteriaCategory {...props} />)

    // then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toStrictEqual('/recherche')
    expect(header.prop('history')).toStrictEqual(props.history)
    expect(header.prop('location')).toStrictEqual(props.history.location)
    expect(header.prop('match')).toStrictEqual(props.match)
    expect(header.prop('title')).toStrictEqual(props.title)
  })

  it('should render a Criteria component with the right props', () => {
    // when
    const wrapper = shallow(<CriteriaCategory {...props} />)

    // then
    const criteria = wrapper.find(Criteria)
    expect(criteria.prop('activeCriterionLabel')).toStrictEqual(props.activeCriterionLabel)
    expect(criteria.prop('backTo')).toStrictEqual(props.backTo)
    expect(criteria.prop('criteria')).toStrictEqual(props.criteria)
    expect(criteria.prop('history')).toStrictEqual(props.history)
    expect(criteria.prop('match')).toStrictEqual(props.match)
    expect(criteria.prop('onCriterionSelection')).toStrictEqual(props.onCriterionSelection)
    expect(criteria.prop('title')).toStrictEqual(props.title)
  })
})
