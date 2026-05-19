import { screen } from '@testing-library/react'

import * as useCurrentUserPermissionsModule from '@/commons/auth/useCurrentUserPermissions'
import { makeUserPermissions } from '@/commons/utils/factories/authFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { makeUserSliceState } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdministrationLayout } from './AdministrationLayout'

const renderAdministrationLayout = (offererCount = 1) => {
  const offererNames = Array.from({ length: offererCount }, (_, i) => ({
    ...defaultGetOffererResponseModel,
    id: i + 1,
    name: `Offerer ${i + 1}`,
  }))

  renderWithProviders(null, {
    routes: [
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
    ],
    initialRouterEntries: ['/administration/donnees-activite/individuel'],
    storeOverrides: {
      user: makeUserSliceState({ offererNames }),
    },
  })
}

describe('AdministrationLayout', () => {
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
  })
})
