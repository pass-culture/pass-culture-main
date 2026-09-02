import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import { type BankAccountResponseModel, InvoiceStatus } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
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

import { DOWNLOAD_REIMBURSEMENTS_LABEL } from './constants'
import { MAX_ITEMS_DOWNLOAD } from './InvoiceTable/InvoiceDownloadActionsBar'
import { Component as ReimbursementsInvoices } from './ReimbursementsInvoices'

const mockLogEvent = vi.fn()

vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderReimbursementsInvoices = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  renderWithProviders(<ReimbursementsInvoices />, {
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

const BASE_INVOICES = [
  {
    reference: 'J123456789',
    date: '2022-11-02',
    amount: 100,
    url: 'J123456789.invoice',
    status: InvoiceStatus.PENDING,
  },
  {
    reference: 'J666666666',
    date: '2022-11-03',
    amount: -50,
    url: 'J666666666.invoice',
    status: InvoiceStatus.PAID,
  },
  {
    reference: 'J987654321',
    date: '2023-10-02',
    amount: 75,
    url: 'J987654321.invoice',
    status: InvoiceStatus.PENDING_PAYMENT,
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
    vi.spyOn(api, 'getOffererBankAccountsAndAttachedVenues').mockResolvedValue({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render a table with invoices', async () => {
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getInvoicesV2).toHaveBeenNthCalledWith(1, {
      query: {
        offererId: 1,
        periodBeginningDate: '2020-11-15',
        periodEndingDate: '2020-12-15',
      },
    })
    expect(await screen.findAllByRole('row')).toHaveLength(4)
    expect(screen.queryAllByRole('columnheader')).toHaveLength(6)

    // first line
    expect(
      screen.getByRole('checkbox', {
        name: 'Sélectionner la ligne du 02/11/2022',
      })
    ).toBeInTheDocument()
    expect(screen.getByText('J123456789')).toBeInTheDocument()
    expect(screen.getByText(/\+ 100,00/)).toBeInTheDocument()

    // second line
    expect(
      screen.getByRole('checkbox', {
        name: 'Sélectionner la ligne du 03/11/2022',
      })
    ).toBeInTheDocument()
    expect(screen.getByText('J666666666')).toBeInTheDocument()
    expect(screen.getByText(/- 50,00/)).toBeInTheDocument()

    // third line
    expect(
      screen.getByRole('checkbox', {
        name: 'Sélectionner la ligne du 02/10/2023',
      })
    ).toBeInTheDocument()
    expect(screen.getByText('J987654321')).toBeInTheDocument()
    expect(screen.getByText(/\+ 75,00/)).toBeInTheDocument()
  })

  it('should display the invoice table', async () => {
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue([
      {
        reference: 'J123456789',
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        status: InvoiceStatus.PAID,
      },
      {
        reference: 'J666666666',
        date: '2022-11-03',
        amount: -50,
        url: 'J666666666.invoice',
        status: InvoiceStatus.PAID,
      },
    ])

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText('Aucun justificatif ne correspond à votre recherche')
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('cell', { name: 'Remboursement' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', {
        name: 'Sélectionner la ligne du 02/11/2022',
      })
    ).toBeInTheDocument()

    expect(screen.getByText('Trop perçu')).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', {
        name: 'Sélectionner la ligne du 03/11/2022',
      })
    ).toBeInTheDocument()
  })

  it('should render no invoice yet information block', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue([])
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: false })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByText('Aucun justificatif ne correspond à votre recherche')
    ).not.toBeInTheDocument()
    expect(
      screen.getByText('Aucun justificatif pour le moment')
    ).toBeInTheDocument()
  })

  it('should render error block', async () => {
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockRejectedValue([])

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })

  it('should display invoice banner', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText(
        /Nous remboursons en un virement toutes les réservations validées entre le 1ᵉʳ et le 15 du mois/
      )
    ).toBeInTheDocument()
  })

  it('should not disable filters', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByLabelText('Type de justificatif')).toBeEnabled()
    expect(screen.getByLabelText('Début de la période')).toBeEnabled()
    expect(screen.getByLabelText('Fin de la période')).toBeEnabled()
  })

  it('should let perform actions on invoices', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValueOnce([
      {
        reference: 'J123456789',
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        status: InvoiceStatus.PAID,
      },
    ])
    vi.spyOn(api, 'getReimbursementsCsvV2').mockResolvedValueOnce('data')
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })

    fetchMock.mockResponseOnce((request) => {
      if (
        request.url === 'http://localhost:3000/J123456789.invoice' &&
        request.method === 'GET'
      ) {
        return {
          status: 200,
          body: 'Mock PDF Content',
          headers: { 'Content-Type': 'application/pdf' },
        }
      }
      return { status: 404 }
    })

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await user.click(screen.getByRole('button', { name: 'Télécharger' }))
    await user.click(screen.getByText('Télécharger le justificatif (.pdf)'))

    await user.click(screen.getByRole('button', { name: 'Télécharger' }))
    await user.click(screen.getByText(DOWNLOAD_REIMBURSEMENTS_LABEL))
    expect(api.getReimbursementsCsvV2).toHaveBeenCalledWith({
      parseAs: 'blob',
      query: {
        invoicesReferences: ['J123456789'],
      },
    })
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
    const user = userEvent.setup()
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getCombinedInvoices').mockResolvedValue({})
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await user.click(
      screen.getByRole('checkbox', { name: 'Sélectionner toutes les lignes' })
    )

    await user.click(screen.getByText('Télécharger les justificatifs (.pdf)'))

    expect(api.getCombinedInvoices).toHaveBeenCalledTimes(1)
    expect(api.getCombinedInvoices).toHaveBeenNthCalledWith(1, {
      query: {
        invoiceReferences: ['J123456789', 'J666666666', 'J987654321'],
      },
    })
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

  it(`should block download several invoices at same time for more than ${MAX_ITEMS_DOWNLOAD} invoices`, async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(
      new Array(MAX_ITEMS_DOWNLOAD + 1).fill(null).map((_, i) => ({
        reference: `J${i + 1}`,
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        status: InvoiceStatus.PAID,
      }))
    )

    vi.spyOn(api, 'getCombinedInvoices').mockResolvedValueOnce({})

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await user.click(
      screen.getByRole('checkbox', { name: 'Sélectionner toutes les lignes' })
    )

    await user.click(screen.getByText('Télécharger les justificatifs (.pdf)'))

    expect(api.getCombinedInvoices).not.toHaveBeenCalled()
  })

  it('should let download several reimbursment csv at same time', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getReimbursementsCsvV2').mockResolvedValueOnce('data')

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await user.click(
      screen.getByRole('checkbox', { name: 'Sélectionner toutes les lignes' })
    )

    await user.click(screen.getByText(DOWNLOAD_REIMBURSEMENTS_LABEL))

    expect(api.getReimbursementsCsvV2).toHaveBeenCalledTimes(1)
    expect(api.getReimbursementsCsvV2).toHaveBeenNthCalledWith(1, {
      parseAs: 'blob',
      query: {
        invoicesReferences: ['J123456789', 'J666666666', 'J987654321'],
      },
    })
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

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de récupérer les informations relatives à vos comptes bancaires.'
    )
  })

  it('should call api with requested date filters', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()

    const beginPeriod = screen.getByLabelText('Début de la période')
    await user.clear(beginPeriod)
    await user.type(beginPeriod, '2020-11-17')

    const endPeriod = screen.getByLabelText('Fin de la période')
    await user.clear(endPeriod)
    await user.type(endPeriod, '2020-11-19')

    expect(searchButton).toBeEnabled()
    await user.click(searchButton)

    await waitFor(() => {
      expect(api.getInvoicesV2).toHaveBeenCalledTimes(2)
    })

    expect(api.getInvoicesV2).toHaveBeenLastCalledWith({
      query: {
        offererId: 1,
        periodBeginningDate: '2020-11-17',
        periodEndingDate: '2020-11-19',
      },
    })

    await user.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(await screen.findByLabelText('Début de la période')).toHaveValue(
      '2020-11-15'
    )
    expect(screen.getByLabelText('Fin de la période')).toHaveValue('2020-12-15')
  })

  it('should filter by amount type', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    // gitleaks:allow
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await user.selectOptions(
      screen.getByLabelText('Type de justificatif'),
      'POSITIVE_AMOUNT'
    )

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    await user.click(searchButton)

    await waitFor(() => {
      expect(api.getInvoicesV2).toHaveBeenCalledTimes(2)
    })

    expect(api.getInvoicesV2).toHaveBeenLastCalledWith({
      query: {
        offererId: 1,
        periodBeginningDate: '2020-11-15',
        periodEndingDate: '2020-12-15',
        amountPositiveOnly: true,
      },
    })
  })

  it('should display error message and disable search button when beginning date is empty', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const beginPeriod = screen.getByLabelText('Début de la période')
    await user.clear(beginPeriod)

    expect(
      screen.getByText('La date de début est obligatoire')
    ).toBeInTheDocument()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()
  })

  it('should display error message and disable search button when ending date is empty', async () => {
    const user = userEvent.setup()
    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: true })
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)

    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const endPeriod = screen.getByLabelText('Fin de la période')
    await user.clear(endPeriod)

    expect(
      screen.getByText('La date de fin est obligatoire')
    ).toBeInTheDocument()

    const searchButton = screen.getByRole('button', {
      name: 'Lancer la recherche',
    })
    expect(searchButton).toBeDisabled()
  })
})
