import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'
import Icon from '../../../../../../layout/Icon/Icon'
import SeeMore from '../SeeMore'
import { Link } from 'react-router-dom'
import { PANE_LAYOUT } from '../../../domain/layout'

describe('src | components | SeeMore', () => {
  let props

  beforeEach(() => {
    props = {
      isInFirstModule: false,
      isSwitching: false,
      historyPush: jest.fn(),
      layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
      parameters: {
        aroundRadius: null,
        geolocation: { latitude: 1, longitude: 2 },
        hitsPerPage: 2,
        offerCategories: [],
        offerIsDuo: false,
        offerIsNew: false,
        offerTypes: { isDigital: false, isEvent: true, isThing: false },
        priceRange: [],
        searchAround: true,
        tags: [],
      },
      trackClickSeeMore: jest.fn(),
    }
  })

  it('should render a white icon for the see more component when is in the first module', () => {
    // Given
    props.isInFirstModule = true

    // When
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // Then
    const icon = wrapper.find(Icon)
    expect(icon.prop('svg')).toBe('ico-offres-home-white')
  })

  it('should render a purple icon for the see more component when is not in the first module', () => {
    // Given
    props.isInFirstModule = false

    // When
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // Then
    const icon = wrapper.find(Icon)
    expect(icon.prop('svg')).toBe('ico-offres-home-purple')
  })

  it('should render a "En voir plus" label', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // Then
    const label = wrapper.find({ children: 'En voir plus' })
    expect(label).toHaveLength(1)
  })

  it('should redirect to the right url when categories are provided and not search around', () => {
    // Given
    props.parameters = {
      aroundRadius: null,
      geolocation: { latitude: null, longitude: null },
      hitsPerPage: 2,
      offerCategories: ['SPECTACLE', 'CINEMA'],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: true, isThing: false },
      priceRange: [],
      searchAround: false,
      tags: [],
    }
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // When
    const link = wrapper.find(Link)
    link.simulate('click', { preventDefault: jest.fn() })

    // Then
    expect(props.historyPush).toHaveBeenCalledWith({
      parametersFromHome: {
        aroundRadius: null,
        geolocation: { latitude: null, longitude: null },
        hitsPerPage: 2,
        offerCategories: ['SPECTACLE', 'CINEMA'],
        offerIsDuo: false,
        offerIsNew: false,
        offerTypes: { isDigital: false, isEvent: true, isThing: false },
        priceRange: [],
        searchAround: false,
        tags: [],
      },
      pathname: '/recherche/resultats',
      search: '?autour-de=non&categories=SPECTACLE;CINEMA',
    })
  })

  it('should redirect to the right url when geolocation is provided and is search around', () => {
    // Given
    props.parameters = {
      aroundRadius: null,
      geolocation: { latitude: 1, longitude: 2 },
      hitsPerPage: 2,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: true, isThing: false },
      priceRange: [],
      searchAround: true,
      tags: [],
    }
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // When
    const link = wrapper.find(Link)
    link.simulate('click', { preventDefault: jest.fn() })

    // Then
    expect(props.historyPush).toHaveBeenCalledWith({
      parametersFromHome: {
        aroundRadius: null,
        geolocation: { latitude: 1, longitude: 2 },
        hitsPerPage: 2,
        offerCategories: [],
        offerIsDuo: false,
        offerIsNew: false,
        offerTypes: { isDigital: false, isEvent: true, isThing: false },
        priceRange: [],
        searchAround: true,
        tags: [],
      },
      pathname: '/recherche/resultats',
      search: '?autour-de=oui&latitude=1&longitude=2',
    })
  })

  it('should trigger tracking when clicking on link', () => {
    // Given
    props.parameters = {
      aroundRadius: null,
      geolocation: { latitude: 1, longitude: 2 },
      hitsPerPage: 2,
      offerCategories: [],
      offerIsDuo: false,
      offerIsNew: false,
      offerTypes: { isDigital: false, isEvent: true, isThing: false },
      priceRange: [],
      searchAround: true,
      tags: [],
    }
    const wrapper = mount(
      <MemoryRouter>
        <SeeMore {...props} />
      </MemoryRouter>
    )

    // When
    const link = wrapper.find(Link)
    link.simulate('click', { preventDefault: jest.fn() })

    // Then
    expect(props.trackClickSeeMore).toHaveBeenCalledTimes(1)
  })
})
