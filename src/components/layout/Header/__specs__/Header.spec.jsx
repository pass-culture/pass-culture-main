import { render, screen } from '@testing-library/react'
import { shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from 'utils/stubStore'

import * as constants from '../_constants'
import Header from '../Header'

import '@testing-library/jest-dom'

describe('header', () => {
  let props

  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      name: 'fake name',
      offerers: [{}],
      isSmall: false,
    }
  })

  describe('render', () => {
    it('should render a header element with the right css classes when is small', () => {
      // given
      props.isSmall = true

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('navbar is-small')
    })
  })
})

const renderHeader = props => {
  const stubStore = getStubStore({
    data: (state = {}) => state,
  })
  render(
    <Provider store={stubStore}>
      <MemoryRouter>
        <Header {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('navigation menu', () => {
  let props
  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      name: 'Utilisateur',
      offerers: [{ id: '1' }],
    }
  })

  describe('should pluralize Offerer menu link', () => {
    it('should display Structure juridique for a single offerer', () => {
      // when
      renderHeader(props)

      // then
      const singularOffererLink = screen.queryByText('Structure juridique')
      const pluralOffererLink = screen.queryByText('Structures juridiques')
      expect(singularOffererLink).toBeInTheDocument()
      expect(singularOffererLink.closest('a')).toHaveAttribute('href', '/structures')
      expect(pluralOffererLink).not.toBeInTheDocument()
    })

    it('should display Structures juridiques for multiple offerers', () => {
      // given
      props.offerers = [{}, {}]

      // when
      renderHeader(props)

      // then
      const singularOffererLink = screen.queryByText('Structure juridique')
      const pluralOffererLink = screen.queryByText('Structures juridiques')
      expect(singularOffererLink).not.toBeInTheDocument()
      expect(pluralOffererLink).toBeInTheDocument()
      expect(pluralOffererLink.closest('a')).toHaveAttribute('href', '/structures')
    })
  })

  describe('help link', () => {
    it('should display a "help" link in the header', () => {
      // when
      renderHeader(props)

      // then
      const helpLink = screen.queryByText('Aide')
      expect(helpLink.closest('a')).toHaveAttribute(
        'href',
        'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
      )
      expect(helpLink.closest('a')).toHaveAttribute('target', '_blank')
    })
  })

  it('should have link to Guichet', () => {
    // Given
    renderHeader(props)

    // When
    const guichetLink = screen.getByText('Guichet')

    // Then
    expect(guichetLink.closest('a')).toHaveAttribute('href', '/guichet')
  })

  it('should have link to Offres', () => {
    // Given
    renderHeader(props)

    // When
    const guichetLink = screen.getByText('Offres')

    // Then
    expect(guichetLink.closest('a')).toHaveAttribute('href', '/offres')
  })

  it('should have link to Profil', () => {
    // Given
    renderHeader(props)

    // When
    const guichetLink = screen.getByText('Profil')

    // Then
    expect(guichetLink.closest('a')).toHaveAttribute('href', '/profil')
  })

  it('should have link to Remboursements', () => {
    // Given
    renderHeader(props)

    // When
    const guichetLink = screen.getByText('Remboursements')

    // Then
    expect(guichetLink.closest('a')).toHaveAttribute('href', '/remboursements')
  })

  it('should have link to Déconnexion', () => {
    // When
    renderHeader(props)

    // Then
    const logOutButton = screen.queryByText('Déconnexion')
    expect(logOutButton).toBeInTheDocument()
  })

  it('should have link to Styleguide when is enabled', () => {
    // Given
    // eslint-disable-next-line
    constants.STYLEGUIDE_ACTIVE = true
    renderHeader(props)

    // Then
    expect(screen.queryByText('Styleguide')).toBeInTheDocument()
  })

  it('should not have link to Styleguide when is disabled', () => {
    // given
    // eslint-disable-next-line
    constants.STYLEGUIDE_ACTIVE = false

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('Styleguide')).not.toBeInTheDocument()
  })

  // reste : les éléments conditionnels (Styleguide et !isSmall)
  // devnote : comment tester que les élements du menu secondaire s'affichent au hover
  // devnote : qui du menu burger ?
})
