import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { ReimbursementContextProvider } from 'context/ReimbursementContext/ReimbursementContext'
import { defautGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Reimbursements from '../Reimbursements'

const renderReimbursements = async (storeOverrides: any) => {
  renderWithProviders(
    <ReimbursementContextProvider>
      <Reimbursements />
    </ReimbursementContextProvider>,
    {
      storeOverrides,
      initialRouterEntries: ['/remboursements/justificatifs'],
    }
  )
}

describe('Reimbursement page', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        currentUser: {
          isAdmin: false,
          hasSeenProTutorials: true,
        },
        initialized: true,
      },
      features: {
        list: [
          { isActive: false, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      },
    }
  })

  it('should render reimbursement page with FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY off', async () => {
    renderReimbursements(store)

    expect(
      screen.getByText('Justificatifs de remboursement')
    ).toBeInTheDocument()
    expect(screen.getByText('Détails des remboursements')).toBeInTheDocument()
    expect(screen.queryByText('Informations bancaires')).not.toBeInTheDocument()

    expect(
      screen.getByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).toBeInTheDocument()
  })
})

describe('Reimbursement page with FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY enabled', () => {
  let selectedOfferer: GetOffererResponseModel
  let store: any

  beforeEach(() => {
    selectedOfferer = {
      ...defautGetOffererResponseModel,
    }

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 1,
          name: 'first offerer',
        },
      ],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(selectedOfferer)

    store = {
      user: {
        currentUser: {
          isAdmin: false,
          hasSeenProTutorials: true,
        },
        initialized: true,
      },
      features: {
        list: [
          { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      },
    }
  })

  it('should render reimbursement page', async () => {
    renderReimbursements(store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByText(/Justificatifs/)).toBeInTheDocument()
    expect(screen.getByText(/Détails/)).toBeInTheDocument()
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByRole('img', {
        name: 'Une action est requise dans cet onglet',
      })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).not.toBeInTheDocument()
  })

  it('should render breadcrumb with error icon', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...selectedOfferer,
      venuesWithNonFreeOffersWithoutBankAccounts: [2],
    })

    renderReimbursements(store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.getOfferer).toHaveBeenCalledTimes(1)
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    await waitFor(() => {
      expect(
        screen.getByRole('img', {
          name: 'Une action est requise dans cet onglet',
        })
      ).toBeInTheDocument()
    })
  })

  it('should render component even if offererNames is empty', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [],
    })

    renderReimbursements(store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })

  it('should render component on getOffererNames error', async () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})
    renderReimbursements(store)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })
})
