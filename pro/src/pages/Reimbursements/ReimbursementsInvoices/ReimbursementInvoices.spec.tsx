import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import { BankAccountResponseModel } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { defaultBankAccount } from 'commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { ReimbursementsInvoices } from './ReimbursementsInvoices'

const mockLogEvent = vi.fn()

vi.mock('commons/utils/date', async () => ({
  ...(await vi.importActual('commons/utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderReimbursementsInvoices = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  renderWithProviders(<ReimbursementsInvoices />, {
    user,
    ...options,
    storeOverrides: {
      user: { currentUser: user },
      offerer: currentOffererFactory(),
    },
  })
}

const BASE_INVOICES = [
  {
    reference: 'J123456789',
    date: '2022-11-02',
    amount: 100,
    url: 'J123456789.invoice',
    bankAccountLabel: 'First bank account',
    cashflowLabels: ['VIR7', 'VIR5'],
  },
  {
    reference: 'J666666666',
    date: '2022-11-03',
    amount: -50,
    url: 'J666666666.invoice',
    bankAccountLabel: 'Second bank account',
    cashflowLabels: ['VIR4'],
  },
  {
    reference: 'J987654321',
    date: '2023-10-02',
    amount: 75,
    url: 'J987654321.invoice',
    bankAccountLabel: 'First bank account',
    cashflowLabels: ['VIR9, VIR12'],
  },
]

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

describe('reimbursementsWithFilters', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('shoud render a table with invoices', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getInvoicesV2).toHaveBeenNthCalledWith(
      1,
      '2020-11-15',
      '2020-12-15',
      undefined,
      1
    )
    expect((await screen.findAllByRole('row')).length).toEqual(4)
    expect(screen.queryAllByRole('columnheader').length).toEqual(7)

    // first line
    expect(
      screen.getByRole('checkbox', {
        name: 'ligne J123456789',
      })
    ).toBeInTheDocument()
    expect(screen.getAllByText('First bank account')).toHaveLength(2)
    expect(screen.getByText('VIR7')).toBeInTheDocument()
    expect(screen.getByText(/100,00/)).toBeInTheDocument()

    // second line
    expect(
      screen.getByRole('checkbox', { name: 'ligne J666666666' })
    ).toBeInTheDocument()
    expect(screen.getByText('N/A')).toBeInTheDocument()
    expect(screen.getByText(/50,00/)).toBeInTheDocument()

    // third line
    expect(
      screen.getByRole('checkbox', { name: 'ligne J987654321' })
    ).toBeInTheDocument()
    expect(screen.getByText('VIR9, VIR12')).toBeInTheDocument()
    expect(screen.getByText(/75,00/)).toBeInTheDocument()
  })

  it('should display the invoice table', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue([
      {
        reference: 'J123456789',
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        bankAccountLabel: 'First reimbursement point',
        cashflowLabels: ['VIR7', 'VIR5'],
      },
      {
        reference: 'J666666666',
        date: '2022-11-03',
        amount: -50,
        url: 'J666666666.invoice',
        bankAccountLabel: 'Second reimbursement point',
        cashflowLabels: ['VIR4'],
      },
    ])

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText(
        'Aucun justificatif de remboursement trouvé pour votre recherche'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Remboursement')).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: 'ligne J123456789' })
    ).toBeInTheDocument()

    expect(screen.getByText('Trop perçu')).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', { name: 'ligne J666666666' })
    ).toBeInTheDocument()
  })

  it('should render no invoice yet information block', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue([])
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: false })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    // there was a bug were two blocks were displayed
    expect(
      screen.queryByText(
        'Aucun justificatif de remboursement trouvé pour votre recherche'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Vous n’avez pas encore de justificatifs de remboursement disponibles'
      )
    ).toBeInTheDocument()
  })

  it('should render error block', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockRejectedValue([])
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })

  it('should display invoice banner', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText(
        /Nous remboursons en un virement toutes les réservations validées entre le 1ᵉʳ et le 15 du mois/
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('Tous les comptes bancaires')).toBeInTheDocument()
  })

  it('should not disable filter if has invoices', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByLabelText('Compte bancaire')).toBeEnabled()
    expect(screen.getByLabelText('Début de la période')).toBeEnabled()
    expect(screen.getByLabelText('Fin de la période')).toBeEnabled()
  })

  it('should let peform actions on invoices', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValueOnce([
      {
        reference: 'J123456789',
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        bankAccountLabel: 'First reimbursement point',
        cashflowLabels: ['VIR7', 'VIR5'],
      },
    ])
    vi.spyOn(api, 'getReimbursementsCsvV2')

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Téléchargement des justificatifs' })
    )
    await userEvent.click(
      screen.getByText('Télécharger le justificatif comptable (.pdf)')
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Téléchargement des justificatifs' })
    )
    await userEvent.click(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    )
    expect(api.getReimbursementsCsvV2).toHaveBeenCalledWith(['J123456789'])
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_INVOICES_DOWNLOAD,
      expect.objectContaining({
        fileType: 'justificatif',
        filesCount: 1,
        buttonType: 'unique',
      })
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_INVOICES_DOWNLOAD,
      expect.objectContaining({
        fileType: 'details',
        filesCount: 1,
        buttonType: 'unique',
      })
    )
  })

  it('should let download several invoices at same time', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'getCombinedInvoices').mockResolvedValue({})
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )

    await userEvent.click(screen.getByText('Télécharger les justificatifs'))

    expect(api.getCombinedInvoices).toHaveBeenCalledTimes(1)
    expect(api.getCombinedInvoices).toHaveBeenNthCalledWith(1, [
      'J123456789',
      'J666666666',
      'J987654321',
    ])
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_INVOICES_DOWNLOAD,
      expect.objectContaining({
        fileType: 'justificatif',
        filesCount: 3,
        buttonType: 'multiple',
      })
    )
  })

  it('should block download several invoices at same time for more than 24 invoices', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(
      new Array(25).fill(null).map((_, i) => ({
        reference: `J${i + 1}`,
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        bankAccountLabel: 'First bank account',
        cashflowLabels: [`VIR${i + 1}`],
      }))
    )

    vi.spyOn(api, 'getCombinedInvoices').mockResolvedValueOnce({})
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )

    await userEvent.click(screen.getByText('Télécharger les justificatifs'))

    expect(api.getCombinedInvoices).not.toHaveBeenCalled()
  })

  it('should let download several reimbursment csv at same time', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'getReimbursementsCsvV2').mockResolvedValueOnce('data')

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.click(
      screen.getByRole('checkbox', { name: 'Tout sélectionner' })
    )

    await userEvent.click(screen.getByText('Télécharger les détails'))

    expect(api.getReimbursementsCsvV2).toHaveBeenCalledTimes(1)
    expect(api.getReimbursementsCsvV2).toHaveBeenNthCalledWith(1, [
      'J123456789',
      'J666666666',
      'J987654321',
    ])
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_INVOICES_DOWNLOAD,
      expect.objectContaining({
        fileType: 'details',
        filesCount: 3,
        buttonType: 'multiple',
      })
    )
  })

  it('should not display Bank account when only one linked', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: [defaultBankAccount],
      managedVenues: [],
    })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.queryByLabelText('Compte bancaire')).not.toBeInTheDocument()
  })

  it('should display Bank account filter when several ', async () => {
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByLabelText('Compte bancaire')).toBeInTheDocument()
  })

  it('should call api with requested filters', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.selectOptions(
      screen.getByLabelText('Compte bancaire'),
      BASE_BANK_ACCOUNTS[0].id.toString()
    )

    const beginPeriod = screen.getByLabelText('Début de la période')
    await userEvent.clear(beginPeriod)
    await userEvent.type(beginPeriod, '2020-11-17')

    const endPeriod = screen.getByLabelText('Fin de la période')
    await userEvent.clear(endPeriod)
    await userEvent.type(endPeriod, '2020-11-19')

    await userEvent.click(screen.getByText('Lancer la recherche'))

    await waitFor(() => {
      expect(api.getInvoicesV2).toHaveBeenCalledTimes(2)
    })

    expect(api.getInvoicesV2).toHaveBeenLastCalledWith(
      '2020-11-17',
      '2020-11-19',
      BASE_BANK_ACCOUNTS[0].id,
      1
    )

    await userEvent.click(screen.getByText('Réinitialiser les filtres'))

    expect(screen.getByLabelText('Compte bancaire')).toHaveValue('all')
    expect(screen.getByLabelText('Début de la période')).toHaveValue(
      '2020-11-15'
    )
    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-12-15')
  })
})
