import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

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

const offererNamesAttached = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: `Offerer 1`,
  },
]

const renderAdministrationLayout = (
  childTitle = "Données d'activité : individuel",
  offererCount = 1,
  options?: RenderWithProvidersOptions
) => {
  const offererNamesAttached = Array.from({ length: offererCount }, (_, i) => ({
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
      offerer: {
        offererNamesAttached,
        combinedOffererNames: offererNamesAttached,
        currentOfferer: offererNamesAttached[0],
      },
    },
    ...options,
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
  it('should render non attached banner if offerer is not attached', () => {
    renderAdministrationLayout(undefined, 2, {
      storeOverrides: {
        offerer: {
          currentOfferer: {
            id: 1,
          },
          offererNamesAttached: [],
          combinedOffererNames: offererNamesAttached,
        },
      },
    })

    expect(
      screen.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })
})
