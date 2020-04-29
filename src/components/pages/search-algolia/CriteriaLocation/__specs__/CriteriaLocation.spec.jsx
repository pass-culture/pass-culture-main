import { shallow } from 'enzyme'
import React from 'react'
import Header from '../../../../layout/Header/Header'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import CriteriaLocation from '../CriteriaLocation'
import { Criteria } from '../../Criteria/Criteria'
import Icon from '../../../../layout/Icon/Icon'

describe('components | CriteriaLocation', () => {
  let props

  beforeEach(() => {
    props = {
      activeCriterionLabel: 'Autour de moi',
      backTo: '/recherche',
      criteria: GEOLOCATION_CRITERIA,
      history: {
        location: {
          pathname: '/recherche/criteres-localisation',
          search: '',
        },
        push: jest.fn(),
        replace: jest.fn(),
      },
      match: {
        params: {},
      },
      onCriterionSelection: jest.fn(),
      title: 'Où',
    }
  })

  it('should render a Header component with the right props', () => {
    // when
    const wrapper = shallow(<CriteriaLocation {...props} />)

    // then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toStrictEqual('/recherche')
    expect(header.prop('closeTo')).toBeNull()
    expect(header.prop('history')).toStrictEqual(props.history)
    expect(header.prop('location')).toStrictEqual(props.history.location)
    expect(header.prop('match')).toStrictEqual(props.match)
    expect(header.prop('title')).toStrictEqual(props.title)
  })

  it('should render a Criteria component with the right props', () => {
    // when
    const wrapper = shallow(<CriteriaLocation {...props} />)

    // then
    const criteria = wrapper.find(Criteria)
    expect(criteria.prop('activeCriterionLabel')).toStrictEqual(props.activeCriterionLabel)
    expect(criteria.prop('backTo')).toStrictEqual(props.backTo)
    expect(criteria.prop('criteria')).toStrictEqual(props.criteria)
    expect(criteria.prop('history')).toStrictEqual(props.history)
    expect(criteria.prop('match')).toStrictEqual(props.match)
    expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
    expect(criteria.prop('title')).toStrictEqual(props.title)
  })

  it('should render an Icon component for the warning message', () => {
    // when
    const wrapper = shallow(<CriteriaLocation {...props} />)

    // then
    const icon = wrapper.find(Icon)
    expect(icon).toHaveLength(1)
    expect(icon.prop('svg')).toBe('ico-alert')
  })

  it('should render a warning message', () => {
    // when
    const wrapper = shallow(<CriteriaLocation {...props} />)

    // then
    const message = wrapper.find({
      children:
        'Seules les offres Sorties et Physiques seront affichées pour une recherche avec une localisation',
    })
    expect(message).toHaveLength(1)
  })

  it('should render a button to redirect to search place page', () => {
    // when
    const wrapper = shallow(<CriteriaLocation {...props} />)

    // then
    const chooseAPlaceButton = wrapper.find({ children: 'Choisir un lieu' })
    expect(chooseAPlaceButton).toHaveLength(1)
  })

  it('should redirect /recherche/criteres-localisation/place when clicking on button', () => {
    // given
    const wrapper = shallow(<CriteriaLocation {...props} />)
    const chooseAPlaceButton = wrapper.find({ children: 'Choisir un lieu' })

    // when
    chooseAPlaceButton.simulate('click')

    // then
    expect(props.history.push).toHaveBeenCalledWith('/recherche/criteres-localisation/place')
  })
})
