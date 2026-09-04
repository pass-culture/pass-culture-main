import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import {
  type BankAccountResponseModel,
  InvoiceStatus,
  type SettlementResponseModel,
  SettlementStatus,
} from '@/apiClient/v1'
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

const BASE_SETTLEMENTS = [
  {
    id: 1,
    label: 'VIR001',
    date: '2024-06-01',
    bankAccount: 'Compte principal',
    status: SettlementStatus.EXECUTED,
    amount: 150,
    invoices: [
      {
        reference: 'J123456789',
        date: '2024-06-01',
        amount: 100,
        url: 'J123456789.invoice',
        status: InvoiceStatus.PAID,
      },
      {
        reference: 'J666666666',
        date: '2024-06-01',
        amount: -50,
        url: 'J666666666.invoice',
        status: InvoiceStatus.PAID,
      },
      {
        reference: 'J987654321',
        date: '2024-06-01',
        amount: 100,
        url: 'J987654321.invoice',
        status: InvoiceStatus.PAID,
      },
    ],
  },
] as SettlementResponseModel[]

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
      query: { offererId: defaultGetOffererResponseModel.id },
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
})
