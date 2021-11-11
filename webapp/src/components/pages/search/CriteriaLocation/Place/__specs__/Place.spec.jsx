import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import Header from '../../../../../layout/Header/Header'
import Place from '../Place'
import { fetchPlaces } from '../../../../../../vendor/api-geo/placesService'
import { Router } from 'react-router'

jest.mock('../../../../../../vendor/api-geo/placesService', () => ({
  fetchPlaces: jest.fn(),
}))
jest.mock('lodash.debounce', () => jest.fn(callback => callback))
describe('components | Place', () => {
  let props

  beforeEach(() => {
    props = {
      backTo: '/recherche/criteres-localisation',
      history: createBrowserHistory(),
      match: { params: {} },
      onPlaceSelection: jest.fn(),
      title: 'Choisir un lieu',
    }

    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([])
      })
    )
  })

  afterEach(() => {
    fetchPlaces.mockReset()
  })

  it('should render a Header component', () => {
    // When
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )

    // then
    const header = wrapper.find(Header)
    expect(header).toHaveLength(1)
    expect(header.prop('backTo')).toBe('/recherche/criteres-localisation')
    expect(header.prop('extraClassName')).toBe('criteria-header')
    expect(header.prop('history')).toBe(props.history)
    expect(header.prop('location')).toBe(props.history.location)
    expect(header.prop('match')).toStrictEqual({ params: {} })
    expect(header.prop('title')).toBe('Choisir un lieu')
  })

  it('should render an input', () => {
    // When
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )

    // then
    const input = wrapper.find('input')
    expect(input).toHaveLength(1)
    expect(input.prop('type')).toBe('search')
    expect(input.prop('onChange')).toStrictEqual(expect.any(Function))
    expect(input.prop('value')).toStrictEqual('')
  })

  it('should focus on input when component is mounted', () => {
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )

    // then
    const input = wrapper.find('input')
    expect(input).toHaveLength(1)
    expect(input.prop('type')).toBe('search')
    expect(input.prop('onChange')).toStrictEqual(expect.any(Function))
    expect(input.prop('value')).toStrictEqual('')
  })

  it('should fetch places when typing in search input', async () => {
    // given
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Pari' } })

    // then
    expect(fetchPlaces).toHaveBeenCalledWith({ keywords: 'Pari' })
  })

  it('should not render a list of suggested places while typing when no result', async () => {
    // given
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Par' } })

    // then
    const suggestedPlaces = wrapper.find('ul')
    expect(suggestedPlaces).toHaveLength(0)
  })

  it('should render a list of suggested places with department while typing a city name', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Nice',
              department: 'Alpes-Maritimes',
            },
            name: {
              long: 'Nice',
              short: 'Nice',
            },
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            extraData: {
              city: 'Niort',
              department: 'Deux-Sèvres',
            },
            name: {
              long: 'Niort',
              short: 'Niort',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: 'Ni' } })
    wrapper.update()

    // then
    const suggestedPlaces = wrapper.find(Place).find('ul').find('li').find('button')
    expect(suggestedPlaces).toHaveLength(2)

    const firstSuggestedPlace = suggestedPlaces.at(0).find('span')
    expect(firstSuggestedPlace.at(0).text()).toBe('Nice')
    expect(firstSuggestedPlace.at(1).text()).toBe('Alpes-Maritimes')

    const secondSuggestedPlace = suggestedPlaces.at(1).find('span')
    expect(secondSuggestedPlace.at(0).text()).toBe('Niort')
    expect(secondSuggestedPlace.at(1).text()).toBe('Deux-Sèvres')
  })

  it('should render a list of suggested places with city while typing an address', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: "34 avenue de l'opéra, Paris",
              short: "34 avenue de l'opéra",
            },
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            extraData: {
              city: 'Toulouse',
              department: 'Haute-Garonne',
            },
            name: {
              long: '34 avenue Angla, Toulouse',
              short: '34 avenue Angla',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: '34 av' } })
    wrapper.update()

    // then
    const suggestedPlaces = wrapper.find(Place).find('ul').find('li').find('button')
    expect(suggestedPlaces).toHaveLength(2)

    const firstSuggestedPlace = suggestedPlaces.at(0).find('span')
    expect(firstSuggestedPlace.at(0).text()).toBe("34 avenue de l'opéra")
    expect(firstSuggestedPlace.at(1).text()).toBe('Paris')

    const secondSuggestedPlace = suggestedPlaces.at(1).find('span')
    expect(secondSuggestedPlace.at(0).text()).toBe('34 avenue Angla')
    expect(secondSuggestedPlace.at(1).text()).toBe('Toulouse')
  })

  it('should render no suggested places when fetching is in error', async () => {
    // given
    fetchPlaces.mockRejectedValueOnce()
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')

    // When
    await input.simulate('change', { target: { value: '' } })

    // then
    const suggestedPlaces = wrapper.find('ul').find('li').find('button')
    expect(suggestedPlaces).toHaveLength(0)
  })

  it('should render a reset button when keywords are typed', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const inputText = wrapper.find('input')

    // When
    await inputText.simulate('change', { target: { value: 'Par' } })

    // then
    const resetButton = wrapper.find('button[type="reset"]')
    expect(resetButton).toHaveLength(1)
  })

  it('should not render a reset button when no keywords are typed', async () => {
    // When
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )

    // then
    const resetButton = wrapper.find('button[type="reset"]')
    expect(resetButton).toHaveLength(0)
  })

  it('should reset text search input and suggestions when clicking on reset button', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    await wrapper.find('input').simulate('change', { target: { value: 'Par' } })
    const input = wrapper.find(Place).instance().inputRef.current
    jest.spyOn(input, 'focus').mockImplementation(jest.fn())

    // When
    const resetButton = wrapper.find('button[type="reset"]')
    resetButton.simulate('click')

    // then
    const inputText = wrapper.find('input')
    expect(inputText.prop('value')).toBe('')
    const suggestedPlaces = wrapper.find('ul').find('li').find('button')
    expect(suggestedPlaces).toHaveLength(0)
    expect(input.focus).toHaveBeenCalledTimes(1)
  })

  it('should update place and redirect to search main page when clicking on a suggested place', async () => {
    // given
    jest.spyOn(props.history, 'push').mockImplementation(() => jest.fn())
    props.history.location.pathname = '/recherche/criteres-localisation/place'
    props.history.location.search = ''
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            extraData: {
              city: 'Pau',
              department: 'Pyrénées-Atlantiques',
            },
            name: {
              long: 'Pau',
              short: 'Pau',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')
    await input.simulate('change', { target: { value: 'Pari' } })
    await wrapper.update()
    const suggestedPlaces = wrapper.find('ul').find('li').find('button')

    // When
    suggestedPlaces.at(0).simulate('click', {
      currentTarget: {
        value: 0,
      },
    })

    // then
    expect(props.onPlaceSelection).toHaveBeenCalledWith({
      geolocation: {
        latitude: 1,
        longitude: 2,
      },
      extraData: {
        city: 'Paris',
        department: 'Paris',
      },
      name: {
        long: 'Paris',
        short: 'Paris',
      },
    })
    expect(props.history.push).toHaveBeenCalledWith('/recherche')
  })

  it('should update place and redirect to previous page when clicking on a suggested place', async () => {
    // given
    jest.spyOn(props.history, 'push').mockImplementation(() => jest.fn())
    props.history.location.pathname = '/recherche/resultats/filtres/localisation/place'
    props.history.location.search = '?mots-cles=&autour-de=non&categories='
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
          {
            geolocation: {
              latitude: 3,
              longitude: 4,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: "34 avenue de l'opéra, Paris",
              short: "34 avenue de l'opéra",
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find('input')
    await input.simulate('change', { target: { value: 'Pari' } })
    await wrapper.update()
    const suggestedPlaces = wrapper.find('ul').find('li').find('button')

    // When
    suggestedPlaces.at(0).simulate('click', {
      currentTarget: {
        value: 0,
      },
    })

    // then
    expect(props.onPlaceSelection).toHaveBeenCalledWith({
      geolocation: {
        latitude: 1,
        longitude: 2,
      },
      extraData: {
        city: 'Paris',
        department: 'Paris',
      },
      name: {
        long: 'Paris',
        short: 'Paris',
      },
    })
    expect(props.history.push).toHaveBeenCalledWith(
      '/recherche/resultats/filtres?mots-cles=&autour-de=non&categories='
    )
  })

  it('should blur input when scrolling results', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    await wrapper.find('input').simulate('change', { target: { value: 'Par' } })
    const input = wrapper.find(Place).instance().inputRef.current
    jest.spyOn(input, 'blur').mockImplementation(jest.fn())

    // When
    const resultsList = wrapper.find(Place).find('div').at(2)
    resultsList.simulate('scroll')

    // then
    expect(input.blur).toHaveBeenCalledTimes(1)
  })

  it('should blur input when submitting form', async () => {
    // given
    fetchPlaces.mockReturnValue(
      new Promise(resolve => {
        resolve([
          {
            geolocation: {
              latitude: 1,
              longitude: 2,
            },
            extraData: {
              city: 'Paris',
              department: 'Paris',
            },
            name: {
              long: 'Paris',
              short: 'Paris',
            },
          },
        ])
      })
    )
    const wrapper = mount(
      <Router history={props.history}>
        <Place {...props} />
      </Router>
    )
    const input = wrapper.find(Place).instance().inputRef.current
    jest.spyOn(input, 'blur').mockImplementation(jest.fn())

    // when
    await wrapper.find('form').simulate('submit', { preventDefault: jest.fn() })

    // then
    expect(input.blur).toHaveBeenCalledTimes(1)
  })
})
