import { shallow } from 'enzyme'
import React from 'react'
import GeolocationCriteria from '../GeolocationCriteria'

describe('src | components | pages | search-algolia | Criteria | GeolocationCriteria', () => {
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
      isGeolocationEnabled: jest.fn(),
    }
  })

  it('should set geolocation for search when "autour de moi" is selected', () => {
    // Given
    const onGeolocationCriterionSelection = jest.fn()
    props.isGeolocationEnabled.mockReturnValue(true)
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeGeolocationLabel="Autour de moi"
        onGeolocationCriterionSelection={onGeolocationCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Autour de moi',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onGeolocationCriterionSelection).toHaveBeenCalledWith('AROUND_ME')
  })

  it('should not set geolocation and alert user to enable geolocation for search when "autour de moi" is selected but geolocation is disabled', () => {
    // Given
    jest.spyOn(window, 'alert').mockImplementationOnce(() => {})
    const onGeolocationCriterionSelection = jest.fn()
    props.isGeolocationEnabled.mockReturnValue(false)
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeGeolocationLabel="Autour de moi"
        onGeolocationCriterionSelection={onGeolocationCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Autour de moi',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onGeolocationCriterionSelection).not.toHaveBeenCalled()
    expect(window.alert).toHaveBeenCalledWith(
      'Veuillez activer la géolocalisation pour voir les offres autour de vous.'
    )
  })

  it('should not set geolocation for search when "Partout" is selected', () => {
    // Given
    const onGeolocationCriterionSelection = jest.fn()
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeGeolocationLabel="Partout"
        onGeolocationCriterionSelection={onGeolocationCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Partout',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onGeolocationCriterionSelection).toHaveBeenCalledWith('EVERYWHERE')
  })
})
