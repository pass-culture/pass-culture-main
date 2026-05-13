import { screen } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { api } from '@/apiClient/api'
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

const buildRoutes = (): RouteObject[] => [
  {
    path: '/administration',
    Component: AdministrationLayout,
    children: [
      {
        path: 'donnees-activite/individuel',
        element: <div data-testid="outlet-content">Page content</div>,
      },
    ],
  },
]

const offererNamesValidated = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: `Offerer 1`,
  },
]

const renderAdministrationLayout = (
  offererCount = 1,
  options?: RenderWithProvidersOptions
) => {
  const offererNamesValidated = Array.from(
    { length: offererCount },
    (_, i) => ({
      ...defaultGetOffererResponseModel,
      id: i + 1,
      name: `Offerer ${i + 1}`,
    })
  )

  renderWithProviders(null, {
    routes: buildRoutes(),
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedAdminOfferer: offererNamesValidated[0],
        offererNamesValidated,
        offererNames: offererNamesValidated,
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

  it('should not display offerer select when there is only one offerer', () => {
    renderAdministrationLayout(1)

    expect(screen.queryByLabelText('Entité juridique')).not.toBeInTheDocument()
  })

  it('should display offerer select when there are multiple offerers', () => {
    renderAdministrationLayout(2)

    expect(screen.getByLabelText('Entité juridique')).toBeInTheDocument()
  })
  it('should render non attached banner if offerer is not attached', () => {
    renderAdministrationLayout(2, {
      storeOverrides: {
        user: {
          offererNamesValidated: [],
          offererNames: offererNamesValidated,
          selectedAdminOfferer: offererNamesValidated[0],
        },
      },
    })

    expect(
      screen.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
  })
  it('should not render outlet content on getOffererNames error', () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})
    renderAdministrationLayout(2, {
      storeOverrides: {
        user: {
          offererNamesValidated: [],
          offererNames: [],
          selectedAdminOfferer: offererNamesValidated[0],
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
