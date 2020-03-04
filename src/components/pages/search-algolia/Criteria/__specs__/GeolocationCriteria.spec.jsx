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
    const onCriterionSelection = jest.fn()
    props.isGeolocationEnabled.mockReturnValue(true)
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeCriterionLabel="Autour de moi"
        onCriterionSelection={onCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Autour de moi',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onCriterionSelection).toHaveBeenCalledWith('AROUND_ME')
  })

  it('should not set geolocation and alert user to enable geolocation for search when "autour de moi" is selected but geolocation is disabled', () => {
    // Given
    jest.spyOn(window, 'alert').mockImplementationOnce(() => {})
    const onCriterionSelection = jest.fn()
    props.isGeolocationEnabled.mockReturnValue(false)
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeCriterionLabel="Autour de moi"
        onCriterionSelection={onCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Autour de moi',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onCriterionSelection).not.toHaveBeenCalled()
    expect(window.alert).toHaveBeenCalledWith(
      'Veuillez activer la géolocalisation pour voir les offres autour de vous.'
    )
  })

  it('should not set geolocation for search when "Partout" is selected', () => {
    // Given
    const onCriterionSelection = jest.fn()
    const wrapper = shallow(
      <GeolocationCriteria
        {...props}
        activeCriterionLabel="Partout"
        onCriterionSelection={onCriterionSelection}
      />
    )
    const aroundMe = wrapper.find({
      children: 'Partout',
    })
    const aroundMeButton = aroundMe.parent()

    // When
    aroundMeButton.simulate('click')

    // Then
    expect(onCriterionSelection).toHaveBeenCalledWith('EVERYWHERE')
  })
})
