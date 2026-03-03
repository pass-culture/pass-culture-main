import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Reimbursements } from './Reimbursements'

const reimbursementsRoutes = [
  {
    path: '/remboursements',
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

function renderReimbursements(options?: RenderWithProvidersOptions) {
  renderWithProviders(<Reimbursements />, {
    routes: reimbursementsRoutes,
    user: sharedCurrentUserFactory(),
    initialRouterEntries: ['/remboursements'],
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: {
        currentOfferer: {
          ...defaultGetOffererResponseModel,
        },
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
        offerer: {
          currentOfferer: {
            venuesWithNonFreeOffersWithoutBankAccounts: [2],
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

  it('should render component even if offererNames is empty', () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [],
      offerersNamesWithPendingValidation: [],
    })

    renderReimbursements()

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })

  it('should render component on getOffererNames error', () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})
    renderReimbursements()

    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })
})
