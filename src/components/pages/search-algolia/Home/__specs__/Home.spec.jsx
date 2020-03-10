import { mount, shallow } from 'enzyme'
import { createBrowserHistory, createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { Home } from '../Home'

describe('components | Home', () => {
  let props
  beforeEach(() => {
    props = {
      history: {
        push: jest.fn(),
      },
      geolocationCriterion: {
        isSearchAroundMe: false,
        params: {
          label: 'Partout',
          icon: 'ico-globe',
        },
      },
      categoryCriterion: {
        label: 'Toutes les catégories',
        icon: 'ico-gem-stone',
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
    expect(header.prop('closeTo')).toBe('/decouverte')
    expect(header.prop('closeTitle')).toBe('Retourner à la page découverte')
  })

  it('should clear text input when clicking on reset cross', async () => {
    // Given
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

    // When
    resetButton.simulate('click')

    // then
    const expectedMissingResetButton = wrapper
      .findWhere(node => node.prop('type') === 'reset')
      .first()
    const resettedInput = form.find('input').first()
    expect(expectedMissingResetButton).toHaveLength(0)
    expect(resettedInput.instance().value).toBe('')
    expect(resettedInput.is(':focus')).toBe(true)
  })

  it('should redirect to result page without "mots-cles" query param if search is empty', () => {
    // Given
    const wrapper = shallow(<Home {...props} />)
    const form = wrapper.find('form')
    // When
    form.simulate('submit', {
      preventDefault: jest.fn(),
    })

    // Then
    expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats')
  })

  it('should redirect to result page if search is made', () => {
    // Given
    const wrapper = shallow(<Home {...props} />)
    const form = wrapper.find('form')
    const input = form.find('input')

    // When
    input.simulate('change', {
      target: {
        value: 'search keyword',
      },
      preventDefault: jest.fn(),
    })
    form.simulate('submit', {
      preventDefault: jest.fn(),
    })

    // Then
    expect(props.history.push).toHaveBeenCalledWith(
      '/recherche-offres/resultats?mots-cles=search keyword'
    )
  })
})
