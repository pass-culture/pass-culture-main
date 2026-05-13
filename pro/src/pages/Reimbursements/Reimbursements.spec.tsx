import { screen, waitFor } from '@testing-library/react'

import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Reimbursements } from './Reimbursements'

const reimbursementsRoutes = [
  {
    path: '/administration/remboursements',
    Component: Reimbursements,
    children: [
      {
        index: true,
        element: <div data-testid="reimbursements-outlet" />,
        handle: { title: 'Gestion financière - justificatifs' },
      },
    ],
  },
]

const user = sharedCurrentUserFactory()

function renderReimbursements(options?: RenderWithProvidersOptions) {
  renderWithProviders(<Reimbursements />, {
    routes: reimbursementsRoutes,
    initialRouterEntries: ['/administration/remboursements'],
    storeOverrides: {
      user: {
        currentUser: user,
        selectedAdminOfferer: defaultGetOffererResponseModel,
      },
    },
    ...options,
  })
}

describe('Reimbursement page', () => {
  it('should render reimbursement page', () => {
    renderReimbursements()

    expect(screen.getByText(/Justificatifs/)).toBeInTheDocument()
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByRole('img', {
        name: 'Une action est requise dans cet onglet',
      })
    ).not.toBeInTheDocument()
  })

  it('should render breadcrumb with error icon', async () => {
    renderReimbursements({
      storeOverrides: {
        user: {
          currentUser: user,
          selectedAdminOfferer: {
            ...defaultGetOffererResponseModel,
            venuesWithNonFreeOffersWithoutBankAccounts: [2],
            hasBankAccountWithPendingCorrections: true,
          },
        },
      },
    })

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()

    await waitFor(() => {
      expect(
        screen.getByRole('img', {
          name: 'Une action est requise dans cet onglet',
        })
      ).toBeInTheDocument()
    })
  })
})
