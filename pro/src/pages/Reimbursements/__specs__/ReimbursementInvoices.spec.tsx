import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
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
  renderWithProviders(<ReimbursementsInvoices />, {
    storeOverrides,
    ...options,
  })
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
    date: '2022-10-02',
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

describe('reimbursementsWithFilters', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getInvoices').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'getReimbursementPoints').mockResolvedValue(
      BASE_REIMBURSEMENT_POINTS
    )
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
    await waitFor(() => {
      expect(screen.queryAllByRole('row').length).toEqual(4)
    })
    expect(screen.queryAllByRole('columnheader').length).toEqual(5)

    const firstLine = [
      '02/10/2022',
      'First reimbursement point',
      'J987654321',
      'VIR9, VIR12',
      '+75,00&nbsp;€',
    ]
    const secondLine = [
      '02/11/2022',
      'First reimbursement point',
      'J123456789',
      'VIR7',
      '+100,00&nbsp;€',
    ]
    const thirdLine = [
      '03/11/2022',
      'Second reimbursement point',
      'J666666666',
      'N/A',
      '-50,00&nbsp;€',
    ]

    await waitFor(() => {
      const reimbursementCells = screen
        .queryAllByRole('cell')
        .map((cell) => cell.innerHTML)
      expect(reimbursementCells.slice(0, 5)).toEqual(firstLine)
      expect(reimbursementCells[5]).toContain('J987654321.invoice')
      expect(reimbursementCells.slice(6, 11)).toEqual(secondLine)
      expect(reimbursementCells[11]).toContain('J123456789.invoice')
      expect(reimbursementCells.slice(12, 17)).toEqual(thirdLine)
      expect(reimbursementCells[17]).toContain('J666666666.invoice')
    })
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
    await waitFor(() => {
      expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
    })
    expect(reimbursementCells[9].innerHTML).toContain('VIR7')
    expect(reimbursementCells[15].innerHTML).toContain('N/A')
    const orderButton = screen.getAllByRole('img', {
      name: 'Trier par ordre croissant',
    })[3]
    await userEvent.click(orderButton)

    let refreshedCells = screen.queryAllByRole('cell')
    expect(refreshedCells[3].innerHTML).toContain('N/A')
    expect(refreshedCells[9].innerHTML).toContain('VIR7')
    expect(refreshedCells[15].innerHTML).toContain('VIR9, VIR12')

    await userEvent.click(orderButton)
    refreshedCells = screen.queryAllByRole('cell')
    expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
    expect(reimbursementCells[9].innerHTML).toContain('VIR7')
    expect(reimbursementCells[15].innerHTML).toContain('N/A')
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
    expect(
      screen.getByText('Tri par n° de justificatif ascendant activé.')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getAllByRole('img', {
        name: 'Trier par ordre croissant',
      })[2]
    )
    expect(
      screen.getByText('Tri par n° de virement ascendant activé.')
    ).toBeInTheDocument()
  })

  it('should not display invoice banner if FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is off', async () => {
    renderReimbursementsInvoices()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).not.toBeInTheDocument()

    expect(screen.getByLabelText('Point de remboursement')).toBeInTheDocument()
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

    expect(screen.getByLabelText('Compte bancaire')).toBeInTheDocument()
    expect(screen.getByText('Tous les comptes bancaires')).toBeInTheDocument()
  })
})
