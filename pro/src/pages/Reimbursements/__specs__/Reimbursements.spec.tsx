import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { Routes, Route } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { routesReimbursements } from 'app/AppRouter/subroutesReimbursements'
import { ReimbursementContextProvider } from 'context/ReimbursementContext/ReimbursementContext'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { Reimbursements } from '../Reimbursements'

const renderReimbursements = (options?: RenderWithProvidersOptions) => {
  const storeOverrides = {
    user: {
      currentUser: {
        isAdmin: false,
        hasSeenProTutorials: true,
      },
      initialized: true,
    },
  }

  renderWithProviders(
    <ReimbursementContextProvider>
      <Routes>
        <Route path="/remboursements" element={<Reimbursements />}>
          {routesReimbursements.map((route) => (
            <Route key={route.path} path={route.path} element={route.element} />
          ))}
        </Route>
        <Route path="/accueil" element={<>Home Page</>} />
      </Routes>
    </ReimbursementContextProvider>,
    {
      initialRouterEntries: ['/remboursements'],
      storeOverrides,
      ...options,
    }
  )
}

describe('Reimbursement page', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getReimbursementPoints').mockResolvedValue([])
    vi.spyOn(api, 'getBankAccounts').mockResolvedValue([])
  })

  it('should render reimbursement page with FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY off', async () => {
    renderReimbursements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
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

  beforeEach(() => {
    selectedOfferer = {
      ...defaultGetOffererResponseModel,
    }

    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'first offerer',
          allowedOnAdage: true,
        }),
      ],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(selectedOfferer)
    vi.spyOn(api, 'getReimbursementPoints').mockResolvedValue([])
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      bankAccounts: [],
      id: 1,
      managedVenues: [],
    })
  })

  it('should render reimbursement page', async () => {
    renderReimbursements({ features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'] })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Justificatifs/)).toBeInTheDocument()
    expect(screen.getByText(/Détails/)).toBeInTheDocument()
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByRole('img', {
        name: 'Une action est requise dans cet onglet',
      })
    ).not.toBeInTheDocument()
  })

  it('should render breadcrumb with error icon', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...selectedOfferer,
      venuesWithNonFreeOffersWithoutBankAccounts: [2],
    })

    renderReimbursements({ features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'] })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
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

    renderReimbursements({ features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'] })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })

  it('should render component on getOffererNames error', async () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})
    renderReimbursements({ features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'] })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })
})
