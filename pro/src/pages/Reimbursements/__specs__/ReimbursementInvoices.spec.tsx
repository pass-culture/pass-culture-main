import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { BankAccountResponseModel } from 'apiClient/v1'
import { ReimbursementsContextProps } from 'pages/Reimbursements/Reimbursements'
import {
  defaultBankAccount,
  defaultGetOffererResponseModel,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { ReimbursementsInvoices } from '../ReimbursementsInvoices/ReimbursementsInvoices'

vi.mock('utils/date', async () => ({
  ...(await vi.importActual('utils/date')),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const contextData: ReimbursementsContextProps = {
  selectedOfferer: {
    ...defaultGetOffererResponseModel,
    name: 'toto',
    id: 1,
  },
  setSelectedOfferer: function () {},
}
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useOutletContext: () => contextData,
}))

const renderReimbursementsInvoices = (options?: RenderWithProvidersOptions) => {
  renderWithProviders(<ReimbursementsInvoices />, {
    user: sharedCurrentUserFactory(),
    ...options,
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
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
    vi.spyOn(api, 'hasInvoice').mockResolvedValueOnce({ hasInvoice: true })
  })

  it('shoud render a table with invoices', async () => {
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
    expect(screen.queryAllByRole('columnheader').length).toEqual(5)

    const firstLine = [
      '<label class="base-checkbox"><span class="base-checkbox-label-row"><input type="checkbox" class="base-checkbox-input"><span class="base-checkbox-label"></span></span></label>02/11/2022',
      '<span class="document-type-content"><svg class="more-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-more.svg#icon"></use></svg>Remboursement</span>',
      'First bank account',
      'VIR7',
      '+100,00&nbsp;€',
    ]
    const secondLine = [
      '<label class="base-checkbox"><span class="base-checkbox-label-row"><input type="checkbox" class="base-checkbox-input"><span class="base-checkbox-label"></span></span></label>03/11/2022',
      '<span class="document-type-content"><svg class="less-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-less.svg#icon"></use></svg>Trop&nbsp;perçu</span>',
      'Second bank account',
      'N/A',
      '-50,00&nbsp;€',
    ]
    const thirdLine = [
      '<label class="base-checkbox"><span class="base-checkbox-label-row"><input type="checkbox" class="base-checkbox-input"><span class="base-checkbox-label"></span></span></label>02/10/2023',
      '<span class="document-type-content"><svg class="more-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-more.svg#icon"></use></svg>Remboursement</span>',
      'First bank account',
      'VIR9, VIR12',
      '+75,00&nbsp;€',
    ]

    const reimbursementCells = screen
      .getAllByRole('cell')
      .map((cell) => cell.innerHTML)
    expect(reimbursementCells.slice(0, 5)).toEqual(firstLine)
    expect(reimbursementCells.slice(6, 11)).toEqual(secondLine)
    expect(reimbursementCells.slice(12, 17)).toEqual(thirdLine)
  })

  it('should display new invoice table if FF WIP_ENABLE_FINANCE_INCIDENT is enable', async () => {
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

    renderReimbursementsInvoices({
      features: ['WIP_ENABLE_FINANCE_INCIDENT'],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText(
        'Aucun justificatif de remboursement trouvé pour votre recherche'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByText('Remboursement')).toBeInTheDocument()
    expect(screen.getByText('Trop perçu')).toBeInTheDocument()
  })

  it('shoud render no invoice yet information block', async () => {
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

  it('shoud render error block', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockRejectedValue([])
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })

  it('should reorder invoices on order buttons click', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const reimbursementCells = await screen.findAllByRole('cell')
    expect(reimbursementCells[3].innerHTML).toContain('VIR7')
    expect(reimbursementCells[9].innerHTML).toContain('N/A')
    expect(reimbursementCells[15].innerHTML).toContain('VIR9, VIR12')
    const orderButton = screen.getAllByRole('img', {
      name: 'Trier par ordre croissant',
    })[3]
    await userEvent.click(orderButton)

    let refreshedCells = screen.getAllByRole('cell')
    expect(refreshedCells[3].innerHTML).toContain('N/A')
    expect(refreshedCells[9].innerHTML).toContain('VIR7')
    expect(refreshedCells[15].innerHTML).toContain('VIR9, VIR12')

    await userEvent.click(orderButton)
    refreshedCells = screen.getAllByRole('cell')
    expect(reimbursementCells[3].innerHTML).toContain('VIR7')
    expect(reimbursementCells[9].innerHTML).toContain('N/A')
    expect(reimbursementCells[15].innerHTML).toContain('VIR9, VIR12')
  })

  it('should contain sort informations for a11y', async () => {
    renderReimbursementsInvoices({
      features: ['WIP_ENABLE_FINANCE_INCIDENT'],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    // All cases for first column
    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Trier par ordre croissant',
      })[0]
    )
    expect(
      screen.getByText('Tri par date ascendant activé.')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Trier par ordre décroissant',
      })[0]
    )
    expect(
      screen.getByText('Tri par date descendant activé.')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Ne plus trier',
      })[0]
    )
    expect(
      screen.getByText('Tri par date par défaut activé.')
    ).toBeInTheDocument()

    // One case for others columns
    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Trier par ordre croissant',
      })[1]
    )
    expect(
      screen.getByText('Tri par type de document ascendant activé.')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Trier par ordre croissant',
      })[1]
    )
  })

  it('should display invoice banner', async () => {
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

  it('should disable filter if no invoices', async () => {
    vi.spyOn(api, 'getInvoicesV2').mockResolvedValue([])

    vi.spyOn(api, 'hasInvoice').mockResolvedValue({ hasInvoice: false })
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByLabelText('Compte bancaire')).toBeDisabled()
    expect(screen.getByLabelText('Début de la période')).toBeDisabled()
    expect(screen.getByLabelText('Fin de la période')).toBeDisabled()
  })

  it('should not disable filter if has invoices', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByLabelText('Compte bancaire')).toBeEnabled()
    expect(screen.getByLabelText('Début de la période')).toBeEnabled()
    expect(screen.getByLabelText('Fin de la période')).toBeEnabled()
  })

  it('should render even without context', () => {
    vi.spyOn(router, 'useOutletContext').mockReturnValue(undefined)

    renderReimbursementsInvoices()

    expect(screen.queryByLabelText('Compte bancaire')).toBeInTheDocument()
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

    renderReimbursementsInvoices({
      features: ['WIP_ENABLE_FINANCE_INCIDENT'],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    await userEvent.click(screen.getAllByTestId('dropdown-menu-trigger')[0])
    expect(
      screen.getByText('Télécharger le justificatif comptable (.pdf)')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    )
    expect(api.getReimbursementsCsvV2).toHaveBeenCalledWith(['J123456789'])
  })

  it('should let download several invoices at same time', async () => {
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
    vi.spyOn(api, 'getReimbursementsCsvV2').mockResolvedValueOnce({})
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
  })
})
