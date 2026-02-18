import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { defaultGetOffererVenueResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PartnerLayout } from './PartnerLayout'

vi.mock('@/app/AppRouter/utils', async () => ({
  ...(await vi.importActual('@/app/AppRouter/utils')),
  hasNewHomepage: () => false,
}))

const user = sharedCurrentUserFactory()

const buildRoutes = (childPath: string, childTitle: string): RouteObject[] => [
  {
    path: '/',
    Component: PartnerLayout,
    children: [
      {
        path: childPath,
        handle: { title: childTitle },
        element: <div data-testid="outlet-content">Page content</div>,
      },
    ],
  },
]

const renderPartnerLayout = (
  childPath = 'accueil',
  childTitle = 'Espace acteurs culturels'
) => {
  renderWithProviders(null, {
    routes: buildRoutes(childPath, childTitle),
    initialRouterEntries: [`/${childPath}`],
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: defaultGetOffererVenueResponseModel,
      },
    },
  })
}

describe('PartnerLayout', () => {
  it('should render the outlet content', () => {
    renderPartnerLayout()

    expect(screen.getByTestId('outlet-content')).toBeInTheDocument()
  })

  it('should display the legacy heading on /accueil', () => {
    renderPartnerLayout()

    expect(
      screen.getByRole('heading', {
        name: 'Bienvenue sur votre espace partenaire',
      })
    ).toBeInTheDocument()
  })

  it('should display the route handle title as heading for non-homepage routes', () => {
    renderPartnerLayout('reservations', 'Réservations individuelles')

    expect(
      screen.getByRole('heading', {
        name: 'Réservations individuelles',
      })
    ).toBeInTheDocument()
  })
})
