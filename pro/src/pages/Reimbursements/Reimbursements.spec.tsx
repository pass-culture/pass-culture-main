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

const offererNamesAttached = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: `Offerer 1`,
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
        offererNamesAttached: offererNamesAttached,
        combinedOffererNames: offererNamesAttached,
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
            id: 1,
            venuesWithNonFreeOffersWithoutBankAccounts: [2],
          },
          offererNamesAttached: offererNamesAttached,
          combinedOffererNames: offererNamesAttached,
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

  it('should render component even if offererNamesAttached is empty', () => {
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

  it('should render non attached banner if offerer is not attached', () => {
    renderReimbursements({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            id: 1,
            venuesWithNonFreeOffersWithoutBankAccounts: [2],
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
