import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { type BankAccountResponseModel, SettlementStatus } from '@/apiClient/v1'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  defaultBankAccount,
  defaultGetOffererResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Settlements } from './Settlements'

vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const BASE_SETTLEMENTS = [
  {
    id: 1,
    label: 'VIR001',
    date: '2024-06-01',
    bankAccount: 'Compte principal',
    status: SettlementStatus.EXECUTED,
    amount: 150,
    invoicesCount: 3,
  },
] as never

const BASE_BANK_ACCOUNTS: Array<BankAccountResponseModel> = [
  {
    ...defaultBankAccount,
    id: 1,
    label: 'My first bank account',
  },
  {
    ...defaultBankAccount,
    id: 2,
    label: 'My second bank account',
  },
]

const renderSettlements = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  return renderWithProviders(<Settlements />, {
    user,
    ...options,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedAdminOfferer: defaultGetOffererResponseModel,
      },
    },
  })
}

describe('<Settlements />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'hasSettlement').mockResolvedValue({ hasSettlement: true })
    vi.spyOn(api, 'getSettlements').mockResolvedValue(BASE_SETTLEMENTS)
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(await axe(container)).toHaveNoViolations()
  })

  it('fetches and renders the settlements for the selected offerer', async () => {
    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledWith({
      path: { offerer_id: defaultGetOffererResponseModel.id },
    })
    expect(api.hasSettlement).toHaveBeenCalledWith({
      query: { offererId: defaultGetOffererResponseModel.id },
    })
    expect(api.getSettlements).toHaveBeenCalledWith({
      query: {
        offererId: defaultGetOffererResponseModel.id,
        periodBeginningDate: '2020-11-15',
        periodEndingDate: '2020-12-15',
      },
    })
    expect(screen.getByText('VIR001')).toBeInTheDocument()
  })

  it('does not fetch the settlements list and shows the empty state when hasSettlement is false', async () => {
    vi.spyOn(api, 'hasSettlement').mockResolvedValue({ hasSettlement: false })

    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getSettlements).not.toHaveBeenCalled()
    expect(
      screen.getByText('Aucun virement pour le moment')
    ).toBeInTheDocument()
  })

  it('should display error snackbar when getOffererBankAccountsAndAttachedVenues fails', async () => {
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockRejectedValue(
      new Error('Server error')
    )
    const snackBarError = vi.fn()
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))

    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de récupérer les informations relatives à vos comptes bancaires.'
    )
  })

  it('passes hasBankAccount as false when offerer has no bank account', async () => {
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: [],
      managedVenues: [],
    })

    renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getOffererBankAccountsAndAttachedVenues).toHaveBeenCalledWith({
      path: { offerer_id: defaultGetOffererResponseModel.id },
    })
    expect(screen.getByText('Rattacher un compte bancaire')).toBeInTheDocument()
  })

  it('should initialize searchParams with default filters if query params are empty', async () => {
    const { router } = renderSettlements()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await waitFor(() => {
      expect(router.state.location.search).toBe(
        '?periodBeginningDate=2020-11-15&periodEndingDate=2020-12-15'
      )
    })
  })

  it('should fetch settlements with custom filters from searchParams', async () => {
    renderSettlements({
      initialRouterEntries: [
        '/?nameSearch=VIR001&bankAccountId=1&periodBeginningDate=2020-10-01&periodEndingDate=2020-10-31',
      ],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getSettlements).toHaveBeenCalledWith({
      query: {
        offererId: defaultGetOffererResponseModel.id,
        nameSearch: 'VIR001',
        bankAccountId: 1,
        periodBeginningDate: '2020-10-01',
        periodEndingDate: '2020-10-31',
      },
    })
  })

  it('should allow filtering settlements using the filter form', async () => {
    const user = userEvent.setup()
    renderSettlements({
      initialRouterEntries: [
        '/?periodBeginningDate=2020-11-15&periodEndingDate=2020-12-15',
      ],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const nameInput = screen.getByLabelText('N° de virement')
    await user.type(nameInput, 'VIR001')

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    await user.click(searchButton)

    await waitFor(() => {
      expect(api.getSettlements).toHaveBeenLastCalledWith({
        query: {
          offererId: defaultGetOffererResponseModel.id,
          nameSearch: 'VIR001',
          periodBeginningDate: '2020-11-15',
          periodEndingDate: '2020-12-15',
        },
      })
    })
  })

  it('should reset filters when clicking reset button', async () => {
    const user = userEvent.setup()
    const { router } = renderSettlements({
      initialRouterEntries: [
        '/?nameSearch=VIR001&bankAccountId=1&periodBeginningDate=2020-10-01&periodEndingDate=2020-10-31',
      ],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const resetButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    await user.click(resetButton)

    await waitFor(() => {
      expect(router.state.location.search).toBe(
        '?periodBeginningDate=2020-11-15&periodEndingDate=2020-12-15'
      )
    })
  })
})
