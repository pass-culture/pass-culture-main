import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { axe } from 'vitest-axe'

import * as useCurrentUserPermissionsModule from '@/commons/auth/useCurrentUserPermissions'
import * as useOffererNamesQueryModule from '@/commons/hooks/swr/useOffererNamesQuery'
import { makeUserPermissions } from '@/commons/utils/factories/authFactories'
import { getOffererNameFactory } from '@/commons/utils/factories/individualApiFactories'
import { makeUserSliceState } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdministrationLayout } from './AdministrationLayout'

const renderAdministrationLayout = (
  offererCount = 1,
  routeHandle: { title?: string; mainTitle?: string } = {
    title: 'Titre de la page',
  }
) => {
  const offererNames = Array.from({ length: offererCount }, (_, i) =>
    getOffererNameFactory({ id: i + 1, name: `Offerer ${i + 1}` })
  )

  vi.spyOn(useOffererNamesQueryModule, 'useOffererNamesQuery').mockReturnValue({
    data: offererNames,
    isLoading: false,
    isValidating: false,
    error: undefined,
    mutate: vi.fn(),
  } as any)

  return renderWithProviders(null, {
    routes: [
      {
        path: '/administration',
        Component: AdministrationLayout,
        children: [
          {
            path: 'donnees-activite/individuel',
            element: <div data-testid="outlet-content">Page content</div>,
            handle: routeHandle,
          },
        ],
      },
    ],
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    storeOverrides: {
      user: makeUserSliceState({
        offererNames,
        selectedAdminOfferer: { id: 1 } as any,
      }),
    },
  })
}

describe('AdministrationLayout', () => {
  it('should render without accessibility violations', async () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: true })
    )

    const { container } = renderAdministrationLayout(1)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not display offerer select when there is only one offerer', () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: true })
    )

    renderAdministrationLayout(1)

    expect(screen.getByTestId('outlet-content')).toBeInTheDocument()
    expect(
      screen.queryByRole('combobox', { name: 'Entité juridique' })
    ).not.toBeInTheDocument()
  })

  it('should display offerer select when there are multiple offerers', () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: true })
    )

    renderAdministrationLayout(2)

    expect(screen.getByTestId('outlet-content')).toBeInTheDocument()
    expect(
      screen.getByRole('combobox', { name: 'Entité juridique' })
    ).toBeInTheDocument()
  })

  it('should render non attached banner if selected admin offerer is not associated', () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: false })
    )

    renderAdministrationLayout(1)

    expect(
      screen.getByText(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeInTheDocument()
    expect(screen.queryByTestId('outlet-content')).not.toBeInTheDocument()
  })

  it('should render title from route handle title property', () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: true })
    )

    renderAdministrationLayout(1, { title: "Titre de l'onglet" })

    expect(
      screen.getByRole('heading', { level: 1, name: "Titre de l'onglet" })
    ).toBeInTheDocument()
  })

  it('should prioritize mainTitle over title from route handle when both are provided', () => {
    vi.spyOn(
      useCurrentUserPermissionsModule,
      'useCurrentUserPermissions'
    ).mockReturnValue(
      makeUserPermissions({ isSelectedAdminOffererAssociated: true })
    )

    renderAdministrationLayout(1, {
      title: "Titre de l'onglet",
      mainTitle: 'Titre principal de la page',
    })

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'Titre principal de la page',
      })
    ).toBeInTheDocument()
  })
})
