import { shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import Header from '../../../../../layout/Header/Header'
import { Place } from '../Place'
import { fetchPlaces } from '../../../../../../vendor/api-geo/placesService'

jest.mock('../../../../../../vendor/api-geo/placesService', () => ({
  fetchPlaces: jest.fn(),
}))
describe('components | Place', () => {
  let props
  beforeEach(() => {
    props = {
      backTo: '/recherche/criteres-localisation',
      history: createBrowserHistory(),
      match: { params: {} },
      title: 'Choisir un lieu',
      updatePlaceInformations: jest.fn(),
    }

    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([])
      })
    )
  })

  it('should render a Header component', () => {
    // When
    const wrapper = shallow(<Place {...props} />)

    // Then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toBe('/recherche/criteres-localisation')
    expect(header.prop('closeTo')).toBeNull()
    expect(header.prop('extraClassName')).toBe('criteria-header')
    expect(header.prop('history')).toBe(props.history)
    expect(header.prop('location')).toBe(props.history.location)
    expect(header.prop('match')).toStrictEqual({ params: {} })
    expect(header.prop('title')).toBe('Choisir un lieu')
  })

  it('should render an input', () => {
    // When
    const wrapper = shallow(<Place {...props} />)

    // Then
    const input = wrapper.find('input')
    expect(input).toHaveLength(1)
    expect(input.prop('type')).toBe('search')
    expect(input.prop('onChange')).toStrictEqual(expect.any(Function))
    expect(input.prop('value')).toStrictEqual('')
  })

  it('should fetch places when typing in search input', () => {
    // Given
    const wrapper = shallow(<Place {...props} />)
    const input = wrapper.find('input')

    // When
    input.simulate('change', { target: { value: 'Pari' } })

    // Then
    expect(fetchPlaces).toHaveBeenCalledWith({ keywords: 'Pari' })
  })

  it('should not render a list of suggested places while typing when no result', async () => {
    // Given
    const wrapper = shallow(<Place {...props} />)
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Par' } })

    // Then
    const suggestedPlaces = wrapper.find('ul')
    expect(suggestedPlaces).toHaveLength(0)
  })

  it('should render a list of suggested places while typing', async () => {
    // Given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            name: 'Paris 15ème arrondissement',
            extraData: 'Paris',
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            name: '34 avenue de l\'Opéra',
            extraData: 'Paris',
          },
        ])
      })
    )
    const wrapper = shallow(<Place {...props} />)
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Par' } })

    // Then
    const suggestedPlaces = wrapper
      .find('ul')
      .find('li')
      .find('button')
    expect(suggestedPlaces).toHaveLength(2)
    expect(suggestedPlaces.at(0).text()).toBe('Paris 15ème arrondissement Paris')
    expect(suggestedPlaces.at(1).text()).toBe('34 avenue de l\'Opéra Paris')
  })

  it('should update and redirect to parent when clicking on a suggested place', async () => {
    // Given
    jest.spyOn(props.history, 'push').mockImplementation(() => {
    })
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            name: 'Paris 15ème arrondissement',
            extraData: 'Paris',
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            name: '34 avenue de l\'Opéra',
            extraData: 'Paris',
          },
        ])
      })
    )
    const wrapper = shallow(<Place {...props} />)
    const input = wrapper.find('input')
    await input.simulate('change', { target: { value: 'Par' } })
    const suggestedPlaces = wrapper
      .find('ul')
      .find('li')
      .find('button')

    // When
    suggestedPlaces.at(0).simulate('click', {
      target: {
        value: 0,
      },
    })

    // Then
    expect(props.updatePlaceInformations).toHaveBeenCalledWith({
      geolocation: {
        latitude: 1,
        longitude: 2,
      },
      name: 'Paris 15ème arrondissement',
      extraData: 'Paris',
    })
    expect(props.history.push).toHaveBeenCalledWith('/recherche/criteres-localisation')
  })

  it('should render no suggested places when fetching is in error', async () => {
    // Given
    jest.spyOn(props.history, 'push').mockImplementation(() => {})
    fetchPlaces.mockRejectedValueOnce()
    const wrapper = shallow(<Place {...props} />)
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: '' } })

    // Then
    const suggestedPlaces = wrapper
      .find('ul')
      .find('li')
      .find('button')
    expect(suggestedPlaces).toHaveLength(0)
  })
})
