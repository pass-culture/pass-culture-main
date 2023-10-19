import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ReimbursementsInvoices } from '../ReimbursementsInvoices'

vi.mock('utils/date', async () => ({
  ...((await vi.importActual('utils/date')) ?? {}),
  getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderReimbursementsInvoices = async (storeOverrides: any) => {
  renderWithProviders(<ReimbursementsInvoices />, {
    storeOverrides,
  })
}

const BASE_INVOICES = [
  {
    reference: 'J123456789',
    date: '13-02-2022',
    amount: 100,
    url: 'J123456789.invoice',
    reimbursementPointName: 'First reimbursement point',
    cashflowLabels: ['VIR7', 'VIR5'],
  },
  {
    reference: 'J666666666',
    date: '11-03-2022',
    amount: 50,
    url: 'J666666666.invoice',
    reimbursementPointName: 'Second reimbursement point',
    cashflowLabels: ['VIR4'],
  },
  {
    reference: 'J987654321',
    date: '10-02-2022',
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
  let store: any

  beforeEach(() => {
    store = {
      user: {
        currentUser: {
          isAdmin: false,
          hasSeenProTutorials: true,
        },
        initialized: true,
      },
      features: {
        list: [
          { isActive: false, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      },
    }

    vi.spyOn(api, 'getInvoices').mockResolvedValue(BASE_INVOICES)
    vi.spyOn(api, 'getReimbursementPoints').mockResolvedValue(
      BASE_REIMBURSEMENT_POINTS
    )
  })

  it('shoud render a table with invoices', async () => {
    renderReimbursementsInvoices(store)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(api.getInvoices).toBeCalledWith(
      '2020-11-15',
      '2020-12-15',
      undefined
    )
    await waitFor(() => {
      expect(screen.queryAllByRole('row').length).toEqual(4)
    })
    expect(screen.queryAllByRole('columnheader').length).toEqual(5)

    const firstLine = [
      '10-02-2022',
      'First reimbursement point',
      'J987654321',
      'VIR9, VIR12',
      '75&nbsp;€',
    ]
    const secondLine = [
      '11-03-2022',
      'Second reimbursement point',
      'J666666666',
      'VIR4',
      '50&nbsp;€',
    ]
    const thirdLine = [
      '13-02-2022',
      'First reimbursement point',
      'J123456789',
      'VIR7',
      '100&nbsp;€',
    ]

    await waitFor(() => {
      const reimbursementCells = screen
        .queryAllByRole('cell')
        .map((cell) => cell.innerHTML)
      expect(reimbursementCells.slice(0, 5)).toEqual(firstLine)
      expect(reimbursementCells[5]).toContain('J987654321.invoice')
      expect(reimbursementCells.slice(6, 11)).toEqual(secondLine)
      expect(reimbursementCells[11]).toContain('J666666666.invoice')
      expect(reimbursementCells.slice(12, 17)).toEqual(thirdLine)
      expect(reimbursementCells[17]).toContain('J123456789.invoice')
    })
  })

  it('should reorder invoices on order buttons click', async () => {
    renderReimbursementsInvoices(store)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const reimbursementCells = await screen.findAllByRole('cell')
    await waitFor(() => {
      expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
    })
    expect(reimbursementCells[9].innerHTML).toContain('VIR4')
    expect(reimbursementCells[15].innerHTML).toContain('VIR7')
    const orderButton = screen.getAllByRole('img', {
      name: 'Trier par ordre croissant',
    })[3]
    await userEvent.click(orderButton)

    let refreshedCells = screen.queryAllByRole('cell')
    expect(refreshedCells[3].innerHTML).toContain('VIR4')
    expect(refreshedCells[9].innerHTML).toContain('VIR7')
    expect(refreshedCells[15].innerHTML).toContain('VIR9, VIR12')

    await userEvent.click(orderButton)
    refreshedCells = screen.queryAllByRole('cell')
    expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
    expect(reimbursementCells[9].innerHTML).toContain('VIR4')
    expect(reimbursementCells[15].innerHTML).toContain('VIR7')
  })

  it('should not display invoice banner if FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is off', async () => {
    renderReimbursementsInvoices(store)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.queryByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).not.toBeInTheDocument()
  })

  it('should display invoice banner if FF WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is enable', async () => {
    store.features = {
      list: [
        { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
      ],
    }
    renderReimbursementsInvoices(store)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByText(
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      )
    ).toBeInTheDocument()
  })
})
