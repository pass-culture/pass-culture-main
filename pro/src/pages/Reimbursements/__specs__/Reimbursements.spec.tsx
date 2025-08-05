import { api } from 'apiClient/api'
import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { routesReimbursements } from 'app/AppRouter/subroutesReimbursements'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Route, Routes } from 'react-router'

import { Reimbursements, ReimbursementsContextProps } from '../Reimbursements'

const contextData: ReimbursementsContextProps = {
  selectedOfferer: defaultGetOffererResponseModel,
}
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useOutletContext: () => contextData,
}))

const renderReimbursements = () => {
  renderWithProviders(
    <Routes>
      <Route path="/remboursements" element={<Reimbursements />}>
        {routesReimbursements.map((route) => (
          <Route key={route.path} path={route.path} element={route.element} />
        ))}
      </Route>
      <Route path="/accueil" element={<>Home Page</>} />
    </Routes>,
    {
      initialRouterEntries: ['/remboursements'],
      user: sharedCurrentUserFactory(),
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
    }
  )
}

describe('Reimbursement page', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'first offerer',
        }),
      ],
    })

    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      defaultGetOffererResponseModel
    )
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      bankAccounts: [],
      id: 1,
      managedVenues: [],
    })
  })

  it('should render reimbursement page', async () => {
    renderReimbursements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Justificatifs/)).toBeInTheDocument()
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
    expect(
      screen.queryByRole('img', {
        name: 'Une action est requise dans cet onglet',
      })
    ).not.toBeInTheDocument()
  })

  it('should render breadcrumb with error icon', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      venuesWithNonFreeOffersWithoutBankAccounts: [2],
    })

    renderReimbursements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
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

    renderReimbursements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })

  it('should render component on getOffererNames error', async () => {
    vi.spyOn(api, 'listOfferersNames').mockRejectedValue({})
    renderReimbursements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(screen.getByText('Informations bancaires')).toBeInTheDocument()
  })

  it('should not render component on getOfferer error', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValue({})
    renderReimbursements()

    await waitFor(() => {
      expect(
        screen.queryByText('Informations bancaires')
      ).not.toBeInTheDocument()
    })
  })
})
