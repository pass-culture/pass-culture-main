import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdministrationLayout } from './AdministrationLayout'

vi.mock('@/commons/hooks/swr/useOffererNamesQuery', () => ({
  useOffererNamesQuery: () => ({ isLoading: false }),
}))

const user = sharedCurrentUserFactory()

const buildRoutes = (childTitle: string): RouteObject[] => [
  {
    path: '/administration',
    Component: AdministrationLayout,
    children: [
      {
        path: 'donnees-activite/individuel',
        handle: { title: childTitle },
        element: <div data-testid="outlet-content">Page content</div>,
      },
    ],
  },
]

const renderAdministrationLayout = (
  childTitle = "Données d'activité : individuel",
  offererCount = 1
) => {
  const offererNames = Array.from({ length: offererCount }, (_, i) => ({
    ...defaultGetOffererResponseModel,
    id: i + 1,
    name: `Offerer ${i + 1}`,
  }))

  renderWithProviders(null, {
    routes: buildRoutes(childTitle),
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    user,
    storeOverrides: {
      user: { currentUser: user },
      offerer: { offererNames },
    },
  })
}

describe('AdministrationLayout', () => {
  it('should render the outlet content', () => {
    renderAdministrationLayout()

    expect(screen.getByTestId('outlet-content')).toBeInTheDocument()
  })

  it('should display the route handle title as heading', () => {
    renderAdministrationLayout("Données d'activité : individuel")

    expect(
      screen.getByRole('heading', {
        name: "Données d'activité : individuel",
      })
    ).toBeInTheDocument()
  })

  it('should not display offerer select when there is only one offerer', () => {
    renderAdministrationLayout(undefined, 1)

    expect(screen.queryByLabelText('Entité juridique')).not.toBeInTheDocument()
  })

  it('should display offerer select when there are multiple offerers', () => {
    renderAdministrationLayout(undefined, 2)

    expect(screen.getByLabelText('Entité juridique')).toBeInTheDocument()
  })
})
