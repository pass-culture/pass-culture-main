import '@testing-library/jest-dom'

import * as firebaseAnalytics from '@firebase/analytics'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route, Switch } from 'react-router'
import { Link } from 'react-router-dom'

import { AnalyticsContextProvider } from 'context/analyticsContext'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics, { useConfigureFirebase } from 'hooks/useAnalytics'
import { configureTestStore } from 'store/testUtils'

import LogRouteNavigation from '../LogRouteNavigation'

jest.mock('@firebase/analytics', () => {
  return {
    getAnalytics: jest.fn().mockReturnValue('getAnalyticsReturn'),
    initializeAnalytics: jest.fn(),
    setUserId: jest.fn(),
    isSupported: jest.fn().mockResolvedValue(true),
    logEvent: jest.fn(),
  }
})
jest.mock('@firebase/app', () => ({
  initializeApp: jest.fn().mockReturnValue({ setup: true }),
}))

jest.mock('@firebase/remote-config', () => ({
  fetchAndActivate: jest.fn().mockResolvedValue({}),
  getRemoteConfig: jest.fn(),
}))

const FakeApp = ({
  children,
}: {
  children: React.ReactNode
}): JSX.Element | null => {
  useConfigureFirebase('userId')
  const { logEvent } = useAnalytics()
  return <>{logEvent ? children : null}</>
}

const renderLogRouteNavigation = () => {
  const Menu = () => (
    <>
      <Link to="/">Accueil</Link>
      <Link to="/structures">Structures</Link>
      <Link to="/subRouter/firstSubRoute">firstSubRoute</Link>
      <Link to="/subRouter/secondSubRoute">secondSubRoute</Link>
    </>
  )
  return render(
    <AnalyticsContextProvider>
      <Provider store={configureTestStore()}>
        <MemoryRouter>
          <FakeApp>
            <Switch>
              <Route
                path="/"
                exact={true}
                render={() => (
                  <LogRouteNavigation route={{ title: 'Main page title' }}>
                    <Menu />
                    <span>Main page</span>
                  </LogRouteNavigation>
                )}
              />
              <Route
                path="/structures"
                exact={true}
                render={() => (
                  <LogRouteNavigation route={{ title: 'Structure page title' }}>
                    <Menu />
                    <span>Structure page</span>
                  </LogRouteNavigation>
                )}
              />
              <Route
                path="/subRouter"
                render={() => (
                  <LogRouteNavigation
                    route={{
                      title: 'SubRouter page title',
                      hasSubRoutes: true,
                    }}
                  >
                    <Menu />

                    <Switch>
                      <Route
                        path="/subRouter/firstSubRoute"
                        exact={true}
                        render={() => (
                          <LogRouteNavigation
                            route={{ title: 'firstSubRoute page title' }}
                          >
                            <span>firstSubRoute page</span>
                          </LogRouteNavigation>
                        )}
                      />
                      <Route
                        path="/subRouter/secondSubRoute"
                        exact={true}
                        render={() => (
                          <LogRouteNavigation
                            route={{ title: 'secondSubRoute page title' }}
                          >
                            <span>secondSubRoute page</span>
                          </LogRouteNavigation>
                        )}
                      />
                    </Switch>
                  </LogRouteNavigation>
                )}
              />
            </Switch>
          </FakeApp>
        </MemoryRouter>
      </Provider>
    </AnalyticsContextProvider>
  )
}

describe('useLogNavigation', () => {
  it('should log an event on location changes', async () => {
    renderLogRouteNavigation()
    await screen.findByText('Main page')
    expect(firebaseAnalytics.logEvent).toHaveBeenLastCalledWith(
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: '',
        title: 'Main page title - pass Culture Pro',
      }
    )

    await userEvent.click(screen.getByRole('link', { name: 'Structures' }))
    await screen.findByText('Structure page')
    expect(firebaseAnalytics.logEvent).toHaveBeenLastCalledWith(
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: 'Main page title - pass Culture Pro',
        title: 'Structure page title - pass Culture Pro',
      }
    )

    await userEvent.click(screen.getByRole('link', { name: /firstSubRoute/ }))
    await screen.findByText('firstSubRoute page')
    expect(firebaseAnalytics.logEvent).toHaveBeenLastCalledWith(
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: 'Structure page title - pass Culture Pro',
        title: 'firstSubRoute page title - pass Culture Pro',
      }
    )

    await userEvent.click(screen.getByRole('link', { name: 'secondSubRoute' }))
    await screen.findByText('secondSubRoute page')
    expect(firebaseAnalytics.logEvent).toHaveBeenLastCalledWith(
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: 'firstSubRoute page title - pass Culture Pro',
        title: 'secondSubRoute page title - pass Culture Pro',
      }
    )

    await userEvent.click(screen.getByRole('link', { name: 'Accueil' }))
    expect(firebaseAnalytics.logEvent).toHaveBeenLastCalledWith(
      'getAnalyticsReturn',
      Events.PAGE_VIEW,
      {
        from: 'secondSubRoute page title - pass Culture Pro',
        title: 'Main page title - pass Culture Pro',
      }
    )

    expect(firebaseAnalytics.logEvent).toHaveBeenCalledTimes(5)
  })
})
