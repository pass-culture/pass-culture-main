import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { routesSignupJourney } from '@/app/AppRouter/subroutesSignupJourneyMap'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignupJourneyRoutes } from '../SignupJourneyRoutes'

const renderSignupJourneyRoutes = () => {
  renderWithProviders(
    <Routes>
      <Route path="/inscription/structure" element={<SignupJourneyRoutes />}>
        {routesSignupJourney.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche'],
    }
  )
}

describe('SignupJourneyRoutes', () => {
  it('should render component', async () => {
    renderSignupJourneyRoutes()
    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          level: 2,
          name: 'Dites-nous pour quelle structure vous travaillez',
        })
      ).toBeInTheDocument()
    })
  })
})
