import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ReimbursementsInvoices } from '../ReimbursementsInvoices'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getReimbursementPoints: jest.fn(),
    getInvoices: jest.fn(),
  },
}))

const renderReimbursementsInvoices = () => {
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
  beforeEach(() => {
    jest.spyOn(api, 'getInvoices').mockResolvedValue(BASE_INVOICES)
    jest
      .spyOn(api, 'getReimbursementPoints')
      .mockResolvedValue(BASE_REIMBURSEMENT_POINTS)
  })

  it('shoud render a table with invoices', async () => {
    renderReimbursementsInvoices()

    const button = screen.queryByRole('link', {
      name: /Lancer la recherche/i,
    })
    await userEvent.click(button)
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
        .map(cell => cell.innerHTML)
      expect(reimbursementCells.slice(0, 5)).toEqual(firstLine)
      expect(reimbursementCells[5]).toContain('J987654321.invoice')
      expect(reimbursementCells.slice(6, 11)).toEqual(secondLine)
      expect(reimbursementCells[11]).toContain('J666666666.invoice')
      expect(reimbursementCells.slice(12, 17)).toEqual(thirdLine)
      expect(reimbursementCells[17]).toContain('J123456789.invoice')
    })
  })

  it('should reorder invoices on order buttons click', async () => {
    renderReimbursementsInvoices()
    const button = screen.queryByRole('link', {
      name: /Lancer la recherche/i,
    })
    await userEvent.click(button)

    const reimbursementCells = await screen.findAllByRole('cell')
    await waitFor(() => {
      expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
    })
    expect(reimbursementCells[9].innerHTML).toContain('VIR4')
    expect(reimbursementCells[15].innerHTML).toContain('VIR7')
    const orderButton = screen.getByText('N° de virement')
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
})
