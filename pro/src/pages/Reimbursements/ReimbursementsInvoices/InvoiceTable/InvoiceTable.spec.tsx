import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import * as apiModule from 'apiClient/api'
import { InvoiceResponseV2Model } from 'apiClient/v1'
import * as analyticsHook from 'app/App/analytics/firebase'
import * as notificationHook from 'commons/hooks/useNotification'

import { InvoiceTable } from './InvoiceTable'

// Mocks
vi.mock('commons/hooks/useNotification', () => ({
  useNotification: vi.fn(),
}))

vi.mock('app/App/analytics/firebase', () => ({
  useAnalytics: vi.fn(),
}))

vi.mock('commons/hooks/useColumnSorting', async () => {
  const actual = await vi.importActual('commons/hooks/useColumnSorting')
  return {
    ...actual,
    useColumnSorting: vi.fn(() => ({
      currentSortingColumn: null,
      currentSortingMode: 'none',
      onColumnHeaderClick: vi.fn(),
    })),
  }
})

vi.mock('commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
}))

const mockNotify = { error: vi.fn() }
const mockLogEvent = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  vi.spyOn(notificationHook, 'useNotification').mockReturnValue(mockNotify)
  vi.spyOn(analyticsHook, 'useAnalytics').mockReturnValue({
    logEvent: mockLogEvent,
  })
})

const invoices: InvoiceResponseV2Model[] = [
  {
    reference: 'INV-001',
    date: '2024-06-01',
    amount: 150,
    bankAccountLabel: 'Bank A',
    cashflowLabels: ['VIRE-001'],
    url: '',
  },
  {
    reference: 'INV-002',
    date: '2024-05-15',
    amount: -50,
    bankAccountLabel: 'Bank B',
    cashflowLabels: ['VIRE-002'],
    url: '',
  },
]

describe('InvoiceTable', () => {
  it('renders invoice rows correctly', () => {
    render(<InvoiceTable invoices={invoices} />)

    const rows = screen.getAllByTestId('invoice-item-row')
    expect(rows).toHaveLength(invoices.length)
    expect(screen.getByLabelText('Tout sélectionner')).toBeInTheDocument()
  })

  it('checks a single invoice', async () => {
    const user = userEvent.setup()
    render(<InvoiceTable invoices={invoices} />)

    const firstCheckbox = screen.getByLabelText('01/06/2024')
    await user.click(firstCheckbox)

    expect(firstCheckbox).toBeChecked()
  })

  it('toggles "select all" checkbox', async () => {
    const user = userEvent.setup()
    render(<InvoiceTable invoices={invoices} />)

    const selectAll = screen.getByLabelText('Tout sélectionner')
    await user.click(selectAll)

    expect(screen.getByLabelText('01/06/2024')).toBeChecked()
    expect(screen.getByLabelText('15/05/2024')).toBeChecked()

    await user.click(selectAll)

    expect(screen.getByLabelText('01/06/2024')).not.toBeChecked()
    expect(screen.getByLabelText('15/05/2024')).not.toBeChecked()
  })

  it('calls download APIs when clicking buttons', async () => {
    const user = userEvent.setup()

    const getCombinedInvoicesMock = vi
      .spyOn(apiModule.api, 'getCombinedInvoices')
      .mockResolvedValueOnce(new Blob(['dummy-pdf']))

    const getReimbursementsCsvV2Mock = vi
      .spyOn(apiModule.api, 'getReimbursementsCsvV2')
      .mockResolvedValueOnce(new Blob(['dummy-csv']))

    render(<InvoiceTable invoices={invoices} />)

    await user.click(screen.getByLabelText('Tout sélectionner'))

    await user.click(screen.getByText('Télécharger les justificatifs'))
    await user.click(screen.getByText('Télécharger les détails'))

    expect(getCombinedInvoicesMock).toHaveBeenCalledWith(['INV-001', 'INV-002'])
    expect(getReimbursementsCsvV2Mock).toHaveBeenCalledWith([
      'INV-001',
      'INV-002',
    ])
  })

  it('shows error when downloading more than 24 invoices', async () => {
    const user = userEvent.setup()

    const manyInvoices = Array.from({ length: 25 }, (_, i) => ({
      reference: `INV-${i + 1}`,
      date: '2024-06-01',
      amount: 100,
      bankAccountLabel: 'Bank A',
      cashflowLabels: [`CF-${i + 1}`],
      url: '',
    }))

    render(<InvoiceTable invoices={manyInvoices} />)

    await user.click(screen.getByLabelText('Tout sélectionner'))
    await user.click(screen.getByText('Télécharger les justificatifs'))

    expect(mockNotify.error).toHaveBeenCalledWith(
      'Vous ne pouvez pas télécharger plus de 24 documents en une fois.'
    )
  })
})
