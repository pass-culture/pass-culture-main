import { mount, shallow } from 'enzyme'
import { createBrowserHistory, createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { Home } from '../Home'
import { CriterionItem } from '../CriterionItem/CriterionItem'

describe('components | Home', () => {
  let props
  beforeEach(() => {
    props = {
      categoryCriterion: {
        filters: [],
        icon: 'ico-gem-stone',
        label: 'Toutes les catégories',
        facetFilter: '',
      },
      geolocationCriterion: {
        isSearchAroundMe: false,
        params: {
          icon: 'ico-globe',
          label: 'Partout',
          requiresGeolocation: false,
        },
      },
      history: {
        push: jest.fn(),
      },
      sortCriterion: {
        index: '',
        icon: 'ico-random',
        label: 'Au hasard',
        requiresGeolocation: false,
      },
    }
  })

  it('should display magnifying glass icon when current route is /recherche-offres', () => {
    // When
    const wrapper = shallow(<Home {...props} />)

    // then
    const form = wrapper.find('form')
    const magnifyingGlassIcon = form.findWhere(node => node.prop('svg') === 'picto-search').first()
    expect(magnifyingGlassIcon).toHaveLength(1)
  })

  it('should display a close button redirecting to discovery when arriving on search page', () => {
    // Given
    const history = createBrowserHistory()
    history.push('/recherche-offres')
    props.match = {
      params: {},
    }

    // when
    const wrapper = mount(
      <Router history={history}>
        <Home {...props} />
      </Router>
    )

    // then
    const header = wrapper.find(HeaderContainer).first()
    expect(header.prop('title')).toBe('Recherche')
    expect(header.prop('closeTo')).toBe('/decouverte')
    expect(header.prop('closeTitle')).toBe('Retourner à la page découverte')
  })

  it('should clear text input when clicking on reset cross', async () => {
    // given
    const history = createMemoryHistory()
    history.push('/recherche-offres')
    const wrapper = await mount(
      <Router history={history}>
        <Home {...props} />
      </Router>
    )
    const form = wrapper.find('form')
    const input = form.find('input').first()
    input.simulate('change', {
      target: {
        name: 'keywords',
        value: 'typed search',
      },
    })
    const resetButton = wrapper.findWhere(node => node.prop('type') === 'reset').first()

    // when
    resetButton.simulate('click')

    // then
    const expectedMissingResetButton = wrapper
      .findWhere(node => node.prop('type') === 'reset')
      .first()
    const resetInput = form.find('input').first()
    expect(expectedMissingResetButton).toHaveLength(0)
    expect(resetInput.instance().value).toBe('')
    expect(resetInput.is(':focus')).toBe(true)
  })

  it('should redirect to result page when search is triggered with no search around me', () => {
    // given
    props.geolocationCriterion.isSearchAroundMe = false
    props.categoryCriterion.facetFilter = 'CINEMA'
    props.sortCriterion.index = '_by_price'
    const wrapper = shallow(<Home {...props} />)
    const form = wrapper.find('form')
    const input = form.find('input')

    // when
    input.simulate('change', {
      target: {
        value: 'search keyword',
      },
      preventDefault: jest.fn(),
    })
    form.simulate('submit', {
      preventDefault: jest.fn(),
    })

    // then
    expect(props.history.push).toHaveBeenCalledWith({
      pathname: '/recherche-offres/resultats',
      search: '?mots-cles=search keyword&autour-de-moi=non&tri=_by_price&categories=CINEMA',
    })
  })

  it('should redirect to result page when search is triggered with search around me', () => {
    // given
    props.geolocationCriterion.isSearchAroundMe = true
    const wrapper = shallow(<Home {...props} />)
    const form = wrapper.find('form')
    const input = form.find('input')

    // when
    input.simulate('change', {
      target: {
        value: 'search keyword',
      },
      preventDefault: jest.fn(),
    })
    form.simulate('submit', {
      preventDefault: jest.fn(),
    })

    // then
    expect(props.history.push).toHaveBeenCalledWith({
      pathname: '/recherche-offres/resultats',
      search: '?mots-cles=search keyword&autour-de-moi=oui&tri=&categories=',
    })
  })

  it('should render a list of CriterionItem with the right props', () => {
    // when
    const wrapper = shallow(<Home {...props} />)

    // then
    const criterionItems = wrapper.find(CriterionItem)
    expect(criterionItems).toHaveLength(3)
    expect(criterionItems.at(0).prop('icon')).toBe('ico-gem-stone')
    expect(criterionItems.at(0).prop('label')).toBe('Je cherche')
    expect(criterionItems.at(0).prop('linkTo')).toBe('/recherche-offres/criteres-categorie')
    expect(criterionItems.at(0).prop('selectedFilter')).toBe('Toutes les catégories')
    expect(criterionItems.at(1).prop('icon')).toBe('ico-globe')
    expect(criterionItems.at(1).prop('label')).toBe('Où')
    expect(criterionItems.at(1).prop('linkTo')).toBe('/recherche-offres/criteres-localisation')
    expect(criterionItems.at(1).prop('selectedFilter')).toBe('Partout')
    expect(criterionItems.at(2).prop('icon')).toBe('ico-random')
    expect(criterionItems.at(2).prop('label')).toBe('Trier par')
    expect(criterionItems.at(2).prop('linkTo')).toBe('/recherche-offres/criteres-tri')
    expect(criterionItems.at(2).prop('selectedFilter')).toBe('Au hasard')
  })
})
