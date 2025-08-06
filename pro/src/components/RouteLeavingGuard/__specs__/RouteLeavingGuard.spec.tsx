import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Link, Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { RouteLeavingGuard, RouteLeavingGuardProps } from '../RouteLeavingGuard'

const MiniAppTest = () => (
  <div>
    <Link to="/">Home</Link>
    <Link to="/about">About</Link>
    <Link to="/contact">Contact</Link>
    <Routes>
      <Route path="/" element={<div>Home page</div>} />
      <Route path="/about" element={<div>About page</div>} />
      <Route path="/contact" element={<div>Contact page</div>} />
    </Routes>
  </div>
)

const renderRouteLeavingGuard = (props: RouteLeavingGuardProps) => {
  renderWithProviders(
    <>
      <MiniAppTest />
      <RouteLeavingGuard {...props}>{props.children}</RouteLeavingGuard>
    </>
  )
}

describe('components | RouteLeavingGuardCollectiveOfferCreation | RouteLeavingGuard', () => {
  let props: RouteLeavingGuardProps

  beforeEach(() => {
    props = {
      shouldBlockNavigation: () => true,
      children: 'Voulez-vous quitter la page actuelle ?',
      dialogTitle: 'title',
    }
  })

  it('should always display the confirmation modal before redirection', async () => {
    // Given
    renderRouteLeavingGuard(props)

    // When
    const aboutPageLink = screen.getByText('About')
    await userEvent.click(aboutPageLink)

    // Then
    expect(
      screen.getByText('Voulez-vous quitter la page actuelle ?')
    ).toBeInTheDocument()
  })

  it("should not display the confirmation modal before redirection when it's not activated", async () => {
    // Given
    props.shouldBlockNavigation = () => false

    //When
    renderRouteLeavingGuard(props)
    const aboutPageLink = screen.getByText('About')
    await userEvent.click(aboutPageLink)

    //Then
    expect(
      screen.queryByText('Voulez-vous quitter la page actuelle ?')
    ).not.toBeInTheDocument()
    expect(screen.getByText('About page')).toBeInTheDocument()
  })

  it('should be redirected after confirm on dialog', async () => {
    //Given
    renderRouteLeavingGuard(props)

    // When
    const aboutPageLink = screen.getByText('About')
    await userEvent.click(aboutPageLink)
    const confirmRedirectionButton = screen.getByText('Quitter')
    await userEvent.click(confirmRedirectionButton)

    // Then
    expect(screen.queryByText('Home page')).not.toBeInTheDocument()
    expect(screen.getByText('About page')).toBeInTheDocument()
  })

  it('should not be redirected after cancel on dialog', async () => {
    //Given
    renderRouteLeavingGuard(props)
    // When
    const aboutPageLink = screen.getByText('About')
    await userEvent.click(aboutPageLink)
    const cancelRedirectionButton = screen.getByText('Annuler')
    await userEvent.click(cancelRedirectionButton)

    // Then
    expect(screen.queryByText('Home page')).toBeInTheDocument()
    expect(screen.queryByText('About page')).not.toBeInTheDocument()
  })

  it('should display the redirection confirmation modal only when the next location is About page', async () => {
    // Given
    props.shouldBlockNavigation = ({ nextLocation }) => {
      // to fix - no-conditional-in-test
      if (nextLocation.pathname === '/about') {
        return true
      }
      return false
    }

    // When
    renderRouteLeavingGuard(props)
    const contactPageLink = screen.getByText('Contact')
    await userEvent.click(contactPageLink)

    // Then
    expect(screen.queryByText('Home page')).not.toBeInTheDocument()
    expect(screen.getByText('Contact page')).toBeInTheDocument()

    // When
    const aboutPageLink = screen.getByText('About')
    await userEvent.click(aboutPageLink)

    // Then
    expect(
      screen.getByText('Voulez-vous quitter la page actuelle ?')
    ).toBeInTheDocument()
  })
})
