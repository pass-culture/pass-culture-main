import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import SetPasswordConfirmContainer from '../SetPasswordConfirmContainer'

const renderSetPassword = (store, history) =>
  render(
    <Provider store={store}>
      <Router history={history}>
        <Route path="/creation-de-mot-de-passe-confirmation">
          <SetPasswordConfirmContainer />
        </Route>
      </Router>
    </Provider>
  )

describe('src | components | pages | SetPassword', () => {
  let store, history, historyPushSpy
  beforeEach(() => {
    store = configureTestStore()
    history = createBrowserHistory()
    history.push('/creation-de-mot-de-passe-confirmation')
    historyPushSpy = jest.spyOn(history, 'push')
  })
  it('should redirect the user to structure page', async () => {
    // Given

    store = configureTestStore({
      user: { currentUser: { publicName: 'Bosetti' } },
    })
    renderSetPassword(store, history)

    // Then
    expect(historyPushSpy).toHaveBeenCalledWith('/accueil')
  })

  it('should render the default page without redirect', async () => {
    // Given
    renderSetPassword(store, history)

    // Then
    expect(
      screen.getByText('Votre mot de passe a bien été enregistré !')
    ).toBeVisible()
  })

  it('should redirect to login page on link click', async () => {
    // Given
    renderSetPassword(store, history)
    const submitButton = screen.getByText('Se connecter', { selector: 'a' })

    // When
    userEvent.click(submitButton)

    // Then
    await waitFor(() => {
      expect(history.push).toHaveBeenCalledWith('/connexion')
    })
  })

  it('should display error message when error in query params', async () => {
    // Given
    history = createBrowserHistory()
    history.push('/creation-de-mot-de-passe-confirmation?error=unvalid-link')

    // When
    renderSetPassword(store, history)

    // Then
    expect(screen.getByText('Votre lien a expiré !')).toBeVisible()
    expect(screen.getByText('Veuillez contacter notre support')).toBeVisible()
    const link = screen.getByText('Contacter')
    expect(link).toBeVisible()
    expect(link.getAttribute('href')).toBe('mailto:support-pro@passculture.app')
  })
})
