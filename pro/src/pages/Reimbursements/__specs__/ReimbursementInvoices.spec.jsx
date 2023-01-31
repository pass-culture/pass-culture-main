import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route } from 'react-router'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import Reimbursements from '../Reimbursements'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getVenues: jest.fn(),
    getReimbursementPoints: jest.fn(),
    getInvoices: jest.fn(),
  },
}))

const renderReimbursements = props => {
  const storeOverrides = {
    user: {
      currentUser: {
        publicName: 'François',
        isAdmin: false,
        hasSeenProTutorials: true,
      },
      initialized: true,
    },
  }

  renderWithProviders(
    <Route path="/remboursements" exact={false}>
      <Reimbursements {...props} />
    </Route>,
    { storeOverrides, initialRouterEntries: ['/remboursements/justificatifs'] }
  )
}

const BASE_VENUES = [
  {
    id: 'VENUE1',
    managingOffererId: 'MO1',
    name: 'name venue 1',
    offererName: 'Offerer name venue 1',
    publicName: 'Public Name venue 1',
    isVirtual: false,
    bookingEmail: 'fake@email.com',
    withdrawalDetails: '',
  },
  {
    id: 'VENUE2',
    managingOffererId: 'MO1',
    name: 'Offre numérique',
    offererName: 'Offerer name venue 2',
    publicName: '',
    isVirtual: true,
    bookingEmail: '',
    withdrawalDetails: '',
  },
]

const BASE_INVOICES = [
  {
    reference: 'J123456789',
    date: '13-02-2022',
    amount: 100,
    url: 'J123456789.invoice',
    reimbursementPointName: 'First business Unit',
    cashflowLabels: ['VIR7', 'VIR5'],
  },
  {
    reference: 'J666666666',
    date: '11-03-2022',
    amount: 50,
    url: 'J666666666.invoice',
    reimbursementPointName: 'Second business Unit',
    cashflowLabels: ['VIR4'],
  },
  {
    reference: 'J987654321',
    date: '10-02-2022',
    amount: 75,
    url: 'J987654321.invoice',
    reimbursementPointName: 'First business Unit',
    cashflowLabels: ['VIR9, VIR12'],
  },
]

describe('reimbursementsWithFilters', () => {
  let props

  beforeEach(() => {
    props = { currentUser: { isAdmin: false } }
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: BASE_VENUES })
    jest.spyOn(api, 'getInvoices').mockResolvedValue(BASE_INVOICES)
    jest.spyOn(api, 'getReimbursementPoints').mockResolvedValue([])
  })

  it('shoud render a table with invoices', async () => {
    renderReimbursements(props)

    const button = screen.queryByRole('link', {
      name: /Lancer la recherche/i,
    })
    await userEvent.click(button)
    expect(api.getInvoices).toBeCalledWith(
      '2020-11-15',
      '2020-12-15',
      undefined
    )
    expect(screen.queryAllByRole('row').length).toEqual(4)
    expect(screen.queryAllByRole('columnheader').length).toEqual(5)
    const reimbursementCells = screen
      .queryAllByRole('cell')
      .map(cell => cell.innerHTML)
    const first_line = [
      '10-02-2022',
      'First business Unit',
      'J987654321',
      'VIR9, VIR12',
      '75&nbsp;€',
    ]
    const second_line = [
      '11-03-2022',
      'Second business Unit',
      'J666666666',
      'VIR4',
      '50&nbsp;€',
    ]
    const third_line = [
      '13-02-2022',
      'First business Unit',
      'J123456789',
      'VIR7',
      '100&nbsp;€',
    ]
    expect(reimbursementCells.slice(0, 5)).toEqual(first_line)
    expect(reimbursementCells[5]).toContain('J987654321.invoice')
    expect(reimbursementCells.slice(6, 11)).toEqual(second_line)
    expect(reimbursementCells[11]).toContain('J666666666.invoice')
    expect(reimbursementCells.slice(12, 17)).toEqual(third_line)
    expect(reimbursementCells[17]).toContain('J123456789.invoice')
  })

  it('shoud reorder invoices on order buttons click', async () => {
    renderReimbursements(props)
    const button = screen.queryByRole('link', {
      name: /Lancer la recherche/i,
    })
    await userEvent.click(button)

    const reimbursementCells = screen.queryAllByRole('cell')
    expect(reimbursementCells[3].innerHTML).toContain('VIR9, VIR12')
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
