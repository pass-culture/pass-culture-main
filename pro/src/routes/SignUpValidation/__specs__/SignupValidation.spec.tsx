import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'
import * as useCurrentUser from 'components/hooks/useCurrentUser'
import * as useNotification from 'components/hooks/useNotification'

import type { Action, History } from 'history'
import { render, waitFor } from '@testing-library/react'

import type { IUseCurrentUserReturn } from 'components/hooks/useCurrentUser'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import SignUpValidation from '../SignUpValidation'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import { configureTestStore } from 'store/testUtils'
import { createBrowserHistory } from 'history'
import reactRouter from 'react-router'

jest.mock('repository/pcapi/pcapi')
jest.mock('components/hooks/useCurrentUser')
jest.mock('components/hooks/useNotification')

describe('src | components | pages | Signup | validation', () => {
  let history: History
  let store = configureTestStore()
  const mockUseNotification = {
    close: jest.fn(),
    error: jest.fn(),
    pending: jest.fn(),
    information: jest.fn(),
    success: jest.fn(),
  }

  beforeEach(() => {
    store = configureTestStore({
      user: {
        currentUser: null,
      },
      features: {
        list: [{ isActive: true, nameKey: 'ENABLE_PRO_ACCOUNT_CREATION' }],
      },
    })
    history = createBrowserHistory()
    jest.spyOn(reactRouter, 'useParams').mockReturnValue({ token: 'AAA' })
    store = configureTestStore()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
    }))
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {},
    } as IUseCurrentUserReturn)
  })

  afterEach(jest.resetAllMocks)

  it('should redirect to home page if the user is logged in', async () => {
    const validateUser = jest.spyOn(pcapi, 'validateUser')
    const redirect = jest.fn()
    jest.spyOn(reactRouter, 'useHistory').mockImplementation(() => ({
      push: redirect,
      length: 0,
      action: 'REPLACE' as Action,
      location: {
        pathname: '',
        search: '',
        state: '',
        hash: '',
      },
      replace: jest.fn(),
      go: jest.fn(),
      goBack: jest.fn(),
      goForward: jest.fn(),
      block: jest.fn(),
      listen: jest.fn(),
      createHref: jest.fn(),
    }))
    jest.spyOn(useCurrentUser, 'default').mockReturnValue({
      currentUser: {
        id: '123',
      },
    } as IUseCurrentUserReturn)
    // when the user is logged in and lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // then the validity of his token should not be verified
    expect(validateUser).not.toHaveBeenCalled()
    // and he should be redirected to home page
    expect(redirect).toHaveBeenCalledTimes(1)
    expect(redirect).toHaveBeenNthCalledWith(1, '/')
  })

  it('should verify validity of user token and redirect to connexion', async () => {
    const validateUser = jest
      .spyOn(pcapi, 'validateUser')
      .mockResolvedValue(true)
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // then the validity of his token should be verified
    expect(validateUser).toHaveBeenCalledTimes(1)
    expect(validateUser).toHaveBeenNthCalledWith(1, 'AAA')
    // and he should be redirected to signin page
    await waitFor(() => {
      expect(history.location.pathname).toBe('/connexion')
    })
  })

  it('should call media campaign tracker once', () => {
    jest.spyOn(pcapi, 'validateUser').mockResolvedValue(true)
    // when the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // then the media campaign tracker should be called once
    expect(campaignTracker.signUpValidation).toHaveBeenCalledTimes(1)
  })

  it('should display a success message when token verification is successful', async () => {
    jest.spyOn(pcapi, 'validateUser').mockResolvedValue(true)
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      success: notifySuccess,
    }))
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // when his token is successfully validated
    // then a success message should be dispatched
    await waitFor(() => {
      expect(notifySuccess).toHaveBeenNthCalledWith(
        1,
        'Votre compte a été créé. Vous pouvez vous connecter avec les identifiants que vous avez choisis.'
      )
    })
  })

  it('should display an error message when token verification is not successful', async () => {
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...mockUseNotification,
      error: notifyError,
    }))
    jest.spyOn(pcapi, 'validateUser').mockRejectedValue({
      errors: {
        global: ['error1', 'error2'],
      },
    })
    // given the user lands on signup validation page
    render(
      <Provider store={store}>
        <Router history={history}>
          <SignUpValidation />
        </Router>
      </Provider>
    )
    // when his token is not successfully validated
    // then an error message should be dispatched
    await waitFor(() => {
      expect(notifyError).toHaveBeenNthCalledWith(1, ['error1', 'error2'])
    })
  })
})
