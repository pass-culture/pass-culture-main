import '@testing-library/jest-dom'

import { act, fireEvent, render, screen } from '@testing-library/react'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Route, Router, Switch } from 'react-router'
import { Link } from 'react-router-dom'

import RouteLeavingGuard, {
  IRouteLeavingGuardProps,
} from '../RouteLeavingGuard'

const MiniAppTest = () => (
  <div>
    <Link to="/">Home</Link>
    <Link to="/about">About</Link>
    <Link to="/contact">Contact</Link>
    <Switch>
      <Route exact path="/">
        <div>Home page</div>
      </Route>
      <Route path="/about">
        <div>About page</div>
      </Route>
      <Route path="/contact">
        <div>Contact page</div>
      </Route>
    </Switch>
  </div>
)

const renderRouteLeavingGuard = async (
  props: IRouteLeavingGuardProps,
  history: History
) => {
  act(() => {
    render(
      <Router history={history}>
        <MiniAppTest />
        <RouteLeavingGuard {...props}>{props.children}</RouteLeavingGuard>
      </Router>
    )
  })
}

describe('new_components | RouteLeavingGuardOfferCreation | RouteLeavingGuard', () => {
  let props: IRouteLeavingGuardProps
  const history = createBrowserHistory()

  beforeEach(() => {
    history.push('/')
    const shouldBlockReturnValue = { redirectPath: '', shouldBlock: true }
    props = {
      shouldBlockNavigation: () => shouldBlockReturnValue,
      when: true,
      children: 'Voulez-vous quitter la page actuelle ?',
      labelledBy: 'LEAVING_OFFER_CREATION_LABEL_ID',
    }
  })

  it('should always display the confirmation modal before redirection', async () => {
    // Given
    await renderRouteLeavingGuard(props, history)

    // When
    const aboutPageLink = screen.getByText('About')
    await fireEvent.click(aboutPageLink)

    // Then
    expect(
      screen.getByText('Voulez-vous quitter la page actuelle ?')
    ).toBeInTheDocument()
  })

  it("should not display the confirmation model before redirection when it's not activated", async () => {
    // Given
    props.when = false

    //When
    await renderRouteLeavingGuard(props, history)
    const aboutPageLink = screen.getByText('About')
    fireEvent.click(aboutPageLink)

    //Then
    expect(
      screen.queryByText('Voulez-vous quitter la page actuelle ?')
    ).not.toBeInTheDocument()
    expect(screen.getByText('About page')).toBeInTheDocument()
  })

  it('should be redirected after confirm on dialog', async () => {
    //Given
    await renderRouteLeavingGuard(props, history)

    // When
    const aboutPageLink = screen.getByText('About')
    fireEvent.click(aboutPageLink)
    const confirmRedirectionButton = screen.getByText('Quitter')
    fireEvent.click(confirmRedirectionButton)

    // Then
    expect(screen.queryByText('Home page')).not.toBeInTheDocument()
    expect(screen.getByText('About page')).toBeInTheDocument()
  })

  it('should not be redirected after cancel on dialog', async () => {
    //Given
    await renderRouteLeavingGuard(props, history)
    // When
    const aboutPageLink = screen.getByText('About')
    fireEvent.click(aboutPageLink)
    const cancelRedirectionButton = screen.getByText('Annuler')
    fireEvent.click(cancelRedirectionButton)

    // Then
    expect(screen.queryByText('Home page')).toBeInTheDocument()
    expect(screen.queryByText('About page')).not.toBeInTheDocument()
  })

  it('should display the redirection confirmation modal only when the next location is About page', async () => {
    // Given
    props.shouldBlockNavigation = nextLocation => {
      // to fix - no-conditional-in-test
      if (nextLocation.pathname === '/about') {
        return { redirectPath: '', shouldBlock: true }
      }
      return { redirectPath: '', shouldBlock: false }
    }

    // When
    await renderRouteLeavingGuard(props, history)
    const contactPageLink = screen.getByText('Contact')
    fireEvent.click(contactPageLink)

    // Then
    expect(screen.queryByText('Home page')).not.toBeInTheDocument()
    expect(screen.getByText('Contact page')).toBeInTheDocument()

    // When
    const aboutPageLink = screen.getByText('About')
    fireEvent.click(aboutPageLink)

    // Then
    expect(
      screen.getByText('Voulez-vous quitter la page actuelle ?')
    ).toBeInTheDocument()
  })
})
