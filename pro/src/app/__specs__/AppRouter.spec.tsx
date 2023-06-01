import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { Link } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import { AppRouter } from '../AppRouter'

jest.mock('hooks/useAnalytics', () => ({
  __esModule: true,
  useConfigureFirebase: jest.fn(),
  default: () => ({ setLogEvent: jest.fn() }),
}))
window.scrollTo = jest.fn()

jest.spyOn(window, 'scrollTo').mockImplementation()

describe('src | AppRouter', () => {
  it('should redirect to not found page when url is not matching a route', () => {
    const store = configureTestStore()

    render(
      <>
        <div id="root"></div>
        <Provider store={store}>
          <AppRouter routes={[]} />
        </Provider>
      </>
    )

    expect(screen.getByText(/Cette page n’existe pas/)).toBeInTheDocument()
  })

  it('should redirect to login when route is private and user not logged in', async () => {
    const store = configureTestStore({
      user: {
        initialized: false,
        currentUser: null,
      },
    })

    render(
      <>
        <div id="root"></div>
        <Provider store={store}>
          <AppRouter
            routes={[
              {
                path: '/',
                element: (
                  <p>
                    Sub component{' '}
                    <Link to={{ pathname: '/offers' }}>Go to private page</Link>
                  </p>
                ),
                meta: { public: true, withoutLayout: true },
              },
              {
                path: '/connexion',
                element: <p>Login page</p>,
                meta: { public: true, withoutLayout: true },
              },
              { path: '/offers', element: <p>Offers page</p> },
            ]}
          />
        </Provider>
      </>
    )

    await userEvent.click(screen.getByText('Go to private page'))
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })
})
