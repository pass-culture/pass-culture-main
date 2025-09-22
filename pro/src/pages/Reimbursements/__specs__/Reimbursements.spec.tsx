import { screen, waitFor } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import { routesReimbursements } from '@/app/AppRouter/subroutesReimbursements'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  Reimbursements,
  type ReimbursementsContextProps,
} from '../Reimbursements'

const contextData: ReimbursementsContextProps = {
  selectedOfferer: defaultGetOffererResponseModel,
}
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useOutletContext: () => contextData,
}))

const renderReimbursements = (options?: RenderWithProvidersOptions) => {
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
      ...options,
    }
  )
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
