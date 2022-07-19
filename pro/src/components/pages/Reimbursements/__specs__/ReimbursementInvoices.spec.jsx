import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router'
import { render, screen } from '@testing-library/react'

import { Provider } from 'react-redux'
import React from 'react'
import Reimbursements from '../ReimbursementsWithFilters'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getVenuesForOfferer: jest.fn(),
  getInvoices: jest.fn(),
}))

const initialStore = {
  user: {
    currentUser: {
      publicName: 'François',
      isAdmin: false,
      hasSeenProTutorials: true,
    },
  },
}

const renderReimbursements = (store, props) => {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/remboursements/justificatifs']}>
        <Route path="/remboursements" exact={false}>
          <Reimbursements {...props} />
        </Route>
      </MemoryRouter>
    </Provider>
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
    businessUnitName: 'First business Unit',
    cashflowLabels: ['VIR7', 'VIR5'],
  },
  {
    reference: 'J666666666',
    date: '11-03-2022',
    amount: 50,
    url: 'J666666666.invoice',
    businessUnitName: 'Second business Unit',
    cashflowLabels: ['VIR4'],
  },
  {
    reference: 'J987654321',
    date: '10-02-2022',
    amount: 75,
    url: 'J987654321.invoice',
    businessUnitName: 'First business Unit',
    cashflowLabels: ['VIR9, VIR12'],
  },
]

describe('reimbursementsWithFilters', () => {
  let props
  let store

  beforeEach(() => {
    store = configureTestStore(initialStore)
    props = { currentUser: { isAdmin: false } }
    jest.spyOn(pcapi, 'getVenuesForOfferer').mockResolvedValue(BASE_VENUES)
    jest.spyOn(pcapi, 'getInvoices').mockResolvedValue(BASE_INVOICES)
  })

  it('shoud render a table with invoices', async () => {
    renderReimbursements(store, props)

    const button = screen.queryByRole('link', {
      name: /Lancer la recherche/i,
    })
    await userEvent.click(button)
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
    renderReimbursements(store, props)
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
