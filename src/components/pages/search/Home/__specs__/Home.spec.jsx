import { mount } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'
import { CriterionItem } from '../CriterionItem/CriterionItem'
import { Home } from '../Home'

describe('components | Home', () => {
  let history
  let props

  beforeEach(() => {
    history = createMemoryHistory()
    props = {
      categoryCriterion: {
        filters: [],
        icon: 'ico-gem-stone',
        label: 'Toutes les catégories',
        facetFilter: '',
      },
      geolocationCriterion: {
        searchAround: {
          everywhere: false,
          place: false,
          user: false,
        },
        params: {
          icon: 'ico-globe',
          label: 'Partout',
          requiresGeolocation: false,
        },
        place: {
          geolocation: {
            latitude: 59.2,
            longitude: 4.3,
          },
          name: {
            long: "34 avenue de l'opéra, Paris",
            short: "34 avenue de l'opéra",
          },
        },
      },
      userGeolocation: {
        latitude: 40,
        longitude: 41,
      },
    }
  })

  it('should clear text input when clicking on reset cross', () => {
    // given
    history.push('/recherche')
    const wrapper = mountHomeInRouter(props, history)
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

  it('should redirect to result page when search is everywhere', () => {
    // given
    props.geolocationCriterion.searchAround = {
      everywhere: true,
      place: false,
      user: false,
    }
    props.categoryCriterion.facetFilter = 'CINEMA'
    const wrapper = mountHomeInRouter(props, history)
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
    expect(history.location.pathname).toStrictEqual('/recherche/resultats')
    expect(history.location.search).toStrictEqual(
      '?mots-cles=search keyword&autour-de=non&categories=CINEMA&latitude=40&longitude=41'
    )
  })

  it('should redirect to result page when search is around user', () => {
    // given
    props.geolocationCriterion.searchAround = {
      everywhere: false,
      place: false,
      user: true,
    }
    const wrapper = mountHomeInRouter(props, history)
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
    expect(history.location.pathname).toStrictEqual('/recherche/resultats')
    expect(history.location.search).toStrictEqual(
      '?mots-cles=search keyword&autour-de=oui&categories=&latitude=40&longitude=41'
    )
  })

  it('should redirect to result page when search is around place', () => {
    // given
    props.geolocationCriterion.searchAround = {
      everywhere: false,
      place: true,
      user: false,
    }
    const wrapper = mountHomeInRouter(props, history)
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
    expect(history.location.pathname).toStrictEqual('/recherche/resultats')
    expect(history.location.search).toStrictEqual(
      "?mots-cles=search keyword&autour-de=oui&categories=&latitude=59.2&longitude=4.3&place=34 avenue de l'opéra, Paris"
    )
  })

  it('should render a list of CriterionItem with the right props', () => {
    // when
    const wrapper = mountHomeInRouter(props, history)

    // then
    const criterionItems = wrapper.find(CriterionItem)
    expect(criterionItems).toHaveLength(2)
    expect(criterionItems.at(0).prop('icon')).toBe('ico-gem-stone')
    expect(criterionItems.at(0).prop('label')).toBe('Je cherche')
    expect(criterionItems.at(0).prop('linkTo')).toBe('/recherche/criteres-categorie')
    expect(criterionItems.at(0).prop('selectedFilter')).toBe('Toutes les catégories')
    expect(criterionItems.at(1).prop('icon')).toBe('ico-globe')
    expect(criterionItems.at(1).prop('label')).toBe('Où')
    expect(criterionItems.at(1).prop('linkTo')).toBe('/recherche/criteres-localisation')
    expect(criterionItems.at(1).prop('selectedFilter')).toBe('Partout')
  })
})

function mountHomeInRouter(props, history) {
  return mount(
    <Router history={history}>
      <Home
        {...props}
        history={history}
      />
    </Router>
  )
}
