import { fireEvent, render, screen } from '@testing-library/react'
import { shallow } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { signout } from 'repository/pcapi/pcapi'
import { getStubStore } from 'utils/stubStore'

import Icon from '../../Icon'
import Header from '../Header'
import '@testing-library/jest-dom'

jest.mock('repository/pcapi/pcapi', () => {
  return {
    signout: jest.fn()
  }
})

describe('header', () => {
  let props

  beforeEach(() => {
    props = {
      isSmall: false,
      name: 'fake name',
      offerers: [{}],
      whiteHeader: false,
    }
  })

  describe('render', () => {
    it('should render a header element with the right css classes when is not small', () => {
      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('navbar is-primary')
    })

    it('should render a header element with the right css classes when is small', () => {
      // given
      props.isSmall = true

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('navbar is-primary is-small')
    })

    describe('should pluralize offerers menu link', () => {
      it('should display Structure juridique when one offerer', () => {
        // when
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')

        const linkTitle = navLinks
          .at(5)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(8)
        expect(linkTitle).toStrictEqual('Structure juridique')
      })

      it('should display Structures juridiques when many offerers', () => {
        // given
        props.offerers = [{}, {}]

        // when
        const wrapper = shallow(<Header {...props} />)
        const navLinks = wrapper.find('NavLink')
        const linkTitle = navLinks
          .at(5)
          .childAt(1)
          .props().children

        // then
        expect(navLinks).toHaveLength(8)
        expect(linkTitle).toStrictEqual('Structures juridiques')
      })
    })

    describe('help link', () => {
      it('should display a "help" link in the header', () => {
        // when
        const wrapper = shallow(<Header {...props} />)

        // then
        const helpLink = wrapper
          .find('.navbar-menu')
          .find('.navbar-end')
          .find('.navbar-item')
          .at(8)
        expect(helpLink.prop('href')).toBe(
          'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/',
        )
        expect(helpLink.prop('target')).toBe('_blank')
      })

      it('should display a "help" icon and the proper label', () => {
        // when
        const wrapper = shallow(<Header {...props} />)

        // then
        const helpLink = wrapper
          .find('.navbar-menu')
          .find('.navbar-end')
          .find('.navbar-item')
          .at(8)
        const spans = helpLink.find('span')
        const helpIcon = spans.at(0).find(Icon)
        const helpLabel = spans.at(1)
        expect(helpIcon.prop('svg')).toBe('ico-help')
        expect(helpLabel.text()).toBe('Aide')
      })
    })
  })
})


const renderHeader = (props) => {
  const stubStore = getStubStore({
    data: (state = {}) => state,
  })
  render(
    <Provider store={stubStore}>
      <MemoryRouter>
        <Header {...props} />
      </MemoryRouter>
    </Provider>,
  )
}

describe('navigation menu', () => {
  let props
  beforeEach(() => {
    props = {
      dispatch: jest.fn(),
      name: 'Utilisateur',
      offerers: [{id: '1'}]
    }
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
    expect(screen.queryByText('Déconnexion').closest('button')).toBeInTheDocument()
  })

  it.skip('should call api to signout when clicking on signout button', () => {
    // Given
    renderHeader(props)

    // When
    fireEvent.click(screen.getByText('Déconnexion'))

    // Then
    expect(signout).toHaveBeenCalledTimes(1)
  })

  it('should have link to Styleguide when in developpement environment', () => {
    // Given
    renderHeader(props)

    // Then
    expect(screen.queryByText('Styleguide')).toBeInTheDocument()
  })

  it.skip('should not have link to Styleguide when in production environment', () => {
    // Given
    const initialEnvironmentName = process.env.ENVIRONMENT_NAME
    process.env.ENVIRONMENT_NAME = 'production'

    // When
    renderHeader(props)

    // Then
    expect(screen.queryByText('Styleguide')).not.toBeInTheDocument()
    process.env.ENVIRONMENT_NAME = initialEnvironmentName
  })

  // reste : les éléments conditionnels (Styleguide et !whiteHeader)
  // devnote : comment tester que les élements du menu secondaire s'affichent au hover
  // devnote : qui du menu burger ?
})
