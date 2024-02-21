import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { BankAccountResponseModel } from 'apiClient/v1'
import { ReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import {
  defaultBankAccountResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/apiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { ReimbursementsInvoices } from '../ReimbursementsInvoices'

vi.mock('utils/date', async () => ({
  ...((await vi.importActual('utils/date')) ?? {}),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderReimbursementsInvoices = (options?: RenderWithProvidersOptions) => {
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
    <ReimbursementContext.Provider
      value={{
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          name: 'toto',
          id: 1,
        },
        setSelectedOfferer: () => undefined,
      }}
    >
      <ReimbursementsInvoices />
    </ReimbursementContext.Provider>,
    {
      storeOverrides,
      ...options,
    }
  )
}

const BASE_INVOICES = [
  {
    reference: 'J123456789',
    date: '2022-11-02',
    amount: 100,
    url: 'J123456789.invoice',
    reimbursementPointName: 'First reimbursement point',
    cashflowLabels: ['VIR7', 'VIR5'],
  },
  {
    reference: 'J666666666',
    date: '2022-11-03',
    amount: -50,
    url: 'J666666666.invoice',
    reimbursementPointName: 'Second reimbursement point',
    cashflowLabels: ['VIR4'],
  },
  {
    reference: 'J987654321',
    date: '2023-10-02',
    amount: 75,
    url: 'J987654321.invoice',
    reimbursementPointName: 'First reimbursement point',
    cashflowLabels: ['VIR9, VIR12'],
  },
]

const BASE_REIMBURSEMENT_POINTS = [
  {
    id: 1,
    name: 'First reimbursement point',
    publicName: 'My first Reimbursement Point',
  },
  {
    id: 2,
    name: 'Second reimbursement point',
    publicName: 'My second Reimbursement Point',
  },
]

const BASE_BANK_ACCOUNTS: Array<BankAccountResponseModel> = [
  {
    ...defaultBankAccountResponseModel,
    id: 1,
    label: 'My first bank account',
  },
  {
    ...defaultBankAccountResponseModel,
    id: 2,
    label: 'My second bank account',
  },
]

describe('reimbursementsWithFilters', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getInvoices').mockResolvedValueOnce(BASE_INVOICES)
    vi.spyOn(api, 'getReimbursementPoints').mockResolvedValueOnce(
      BASE_REIMBURSEMENT_POINTS
    )
    vi.spyOn(
      api,
      'getOffererBankAccountsAndAttachedVenues'
    ).mockResolvedValueOnce({
      id: 1,
      bankAccounts: BASE_BANK_ACCOUNTS,
      managedVenues: [],
    })
  })

  it('shoud render a table with invoices', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getInvoices).toHaveBeenNthCalledWith(
      1,
      '2020-11-15',
      '2020-12-15',
      undefined
    )
    expect(screen.queryAllByRole('row').length).toEqual(4)
    expect(screen.queryAllByRole('columnheader').length).toEqual(5)

    const firstLine = [
      '02/11/2022',
      '<span class="document-type-content"><svg class="more-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-more.svg#icon"></use></svg>Remboursement</span>',
      'First reimbursement point',
      'VIR7',
      '+100,00&nbsp;€',
    ]
    const secondLine = [
      '03/11/2022',
      '<span class="document-type-content"><svg class="less-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-less.svg#icon"></use></svg>Trop&nbsp;perçu</span>',
      'Second reimbursement point',
      'N/A',
      '-50,00&nbsp;€',
    ]
    const thirdLine = [
      '02/10/2023',
      '<span class="document-type-content"><svg class="more-icon" viewBox="0 0 48 48" aria-hidden="true" width="16"><use xlink:href="/icons/stroke-more.svg#icon"></use></svg>Remboursement</span>',
      'First reimbursement point',
      'VIR9, VIR12',
      '+75,00&nbsp;€',
    ]

    const reimbursementCells = screen
      .getAllByRole('cell')
      .map((cell) => cell.innerHTML)
    expect(reimbursementCells.slice(0, 5)).toEqual(firstLine)
    expect(reimbursementCells[5]).toContain('J123456789.invoice')
    expect(reimbursementCells.slice(6, 11)).toEqual(secondLine)
    expect(reimbursementCells[11]).toContain('J666666666.invoice')
    expect(reimbursementCells.slice(12, 17)).toEqual(thirdLine)
    expect(reimbursementCells[17]).toContain('J987654321.invoice')
  })

  it('should display new invoice table if FF WIP_ENABLE_FINANCE_INCIDENT is enable', async () => {
    vi.spyOn(api, 'getInvoices').mockResolvedValueOnce([
      {
        reference: 'J123456789',
        date: '2022-11-02',
        amount: 100,
        url: 'J123456789.invoice',
        reimbursementPointName: 'First reimbursement point',
        cashflowLabels: ['VIR7', 'VIR5'],
      },
      {
        reference: 'J666666666',
        date: '2022-11-03',
        amount: -50,
        url: 'J666666666.invoice',
        reimbursementPointName: 'Second reimbursement point',
        cashflowLabels: ['VIR4'],
      },
    ])

    renderReimbursementsInvoices({
      features: ['WIP_ENABLE_FINANCE_INCIDENT'],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Remboursement')).toBeInTheDocument()
    expect(screen.getByText('Trop perçu')).toBeInTheDocument()
  })

  it('shoud render no invoice yet information block', async () => {
    vi.spyOn(api, 'getInvoices').mockResolvedValueOnce([])
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

  it('shoud render no result block', async () => {
    vi.spyOn(api, 'getInvoices').mockResolvedValueOnce([])
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByText(
        'Aucun justificatif de remboursement trouvé pour votre recherche'
      )
    ).not.toBeInTheDocument()

    vi.spyOn(api, 'getInvoices').mockResolvedValueOnce([])
    await userEvent.click(screen.getByText('Lancer la recherche'))

    expect(
      screen.getByText(
        'Aucun justificatif de remboursement trouvé pour votre recherche'
      )
    ).toBeInTheDocument()
  })

  it('shoud render error block', async () => {
    vi.spyOn(api, 'getInvoices').mockRejectedValueOnce([])
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
  })

  it('should display reimbursement points', async () => {
    renderReimbursementsInvoices()

    expect(
      (await screen.findByLabelText(/Point de remboursement/)).childElementCount
    ).toEqual(BASE_REIMBURSEMENT_POINTS.length + 1)
    expect(api.getReimbursementPoints).toHaveBeenCalledTimes(1)
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

  it('should not display invoice banner if FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is off', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).not.toBeInTheDocument()

    expect(
      screen.getByLabelText('Point de remboursement *')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Tous les points de remboursement')
    ).toBeInTheDocument()
  })

  it('should display invoice banner if FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is enable', async () => {
    renderReimbursementsInvoices({
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Compte bancaire *')).toBeInTheDocument()
    expect(screen.getByText('Tous les comptes bancaires')).toBeInTheDocument()
  })
})
