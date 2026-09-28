import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { type InvoiceResponseV2Model, InvoiceStatus } from '@/apiClient/v1'
import * as analyticsHook from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useMediaQueryModule from '@/commons/hooks/useMediaQuery'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import * as downloadFileModule from '@/commons/utils/downloadFile'

import {
  DOWNLOAD_INVOICE_LABEL,
  DOWNLOAD_REIMBURSEMENTS_LABEL,
} from '../constants'
import { InvoiceActions } from './InvoiceActions'

vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: vi.fn(),
}))

vi.mock('@/commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getReimbursementsCsvV2: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const mockLogEvent = vi.fn()

const mockInvoice: InvoiceResponseV2Model = {
  reference: 'INV-001',
  date: '2024-06-01',
  amount: 150,
  status: InvoiceStatus.PAID,
  url: 'https://example.com/invoice.pdf',
}

beforeEach(() => {
  vi.spyOn(useMediaQueryModule, 'useMediaQuery').mockReturnValue(false)
  vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
    success: vi.fn(),
    error: snackBarError,
  }))

  vi.spyOn(analyticsHook, 'useAnalytics').mockReturnValue({
    logEvent: mockLogEvent,
  })
})

describe('<InvoiceActions />', () => {
  it('should render without accessibility violations in dropdown mode', async () => {
    const { container } = render(<InvoiceActions invoice={mockInvoice} />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should position the dropdown to the right on desktop', async () => {
    const user = userEvent.setup()
    vi.mocked(useMediaQueryModule.useMediaQuery).mockReturnValue(false)

    render(<InvoiceActions invoice={mockInvoice} />)
    await user.click(screen.getByRole('button', { name: 'Télécharger' }))

    expect(screen.getByRole('menu')).toHaveAttribute('data-side', 'right')
    expect(screen.getByRole('menu')).toHaveAttribute('data-align', 'start')
  })

  it('should position the dropdown below and centered on tablet', async () => {
    const user = userEvent.setup()
    vi.mocked(useMediaQueryModule.useMediaQuery).mockReturnValue(true)

    render(<InvoiceActions invoice={mockInvoice} />)
    await user.click(screen.getByRole('button', { name: 'Télécharger' }))

    expect(screen.getByRole('menu')).toHaveAttribute('data-side', 'bottom')
    expect(screen.getByRole('menu')).toHaveAttribute('data-align', 'center')
  })

  it('should render the menu in the provided portal container', async () => {
    const user = userEvent.setup()
    const portalContainer = document.createElement('div')
    document.body.appendChild(portalContainer)

    render(
      <InvoiceActions invoice={mockInvoice} portalContainer={portalContainer} />
    )
    await user.click(screen.getByRole('button', { name: 'Télécharger' }))

    expect(
      within(portalContainer).getByRole('menuitem', {
        name: DOWNLOAD_INVOICE_LABEL,
      })
    ).toBeInTheDocument()
  })

  it('should display error message when PDF download fails', async () => {
    const user = userEvent.setup()

    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'))

    render(<InvoiceActions invoice={mockInvoice} />)

    const triggerButton = screen.getByRole('button', { name: 'Télécharger' })
    await user.click(triggerButton)

    const pdfMenuItem = screen.getByRole('menuitem', {
      name: DOWNLOAD_INVOICE_LABEL,
    })
    await user.click(pdfMenuItem)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    })
    expect(downloadFileModule.downloadFile).not.toHaveBeenCalled()
  })

  it('should successfully download PDF when fetch succeeds', async () => {
    const user = userEvent.setup()

    const mockBlob = new Blob(['dummy-pdf-content'], {
      type: 'application/pdf',
    })
    global.fetch = vi.fn().mockResolvedValueOnce({
      blob: () => Promise.resolve(mockBlob),
    } as Response)

    render(<InvoiceActions invoice={mockInvoice} />)

    const triggerButton = screen.getByRole('button', { name: 'Télécharger' })
    await user.click(triggerButton)

    const pdfMenuItem = screen.getByRole('menuitem', {
      name: DOWNLOAD_INVOICE_LABEL,
    })
    await user.click(pdfMenuItem)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(mockInvoice.url)
    })
    expect(downloadFileModule.downloadFile).toHaveBeenCalledWith(
      mockBlob,
      'justificatif_comptable.pdf'
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_INVOICES_DOWNLOAD,
      {
        fileType: 'justificatif',
        filesCount: 1,
        buttonType: 'unique',
      }
    )
    expect(snackBarError).not.toHaveBeenCalled()
  })

  it('should display error message when CSV download fails', async () => {
    const user = userEvent.setup()

    vi.mocked(api.getReimbursementsCsvV2).mockRejectedValueOnce(
      new Error('Network error')
    )

    render(<InvoiceActions invoice={mockInvoice} />)

    const triggerButton = screen.getByRole('button', { name: 'Télécharger' })
    await user.click(triggerButton)

    const csvMenuItem = screen.getByRole('menuitem', {
      name: DOWNLOAD_REIMBURSEMENTS_LABEL,
    })
    await user.click(csvMenuItem)

    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    })
    expect(downloadFileModule.downloadFile).not.toHaveBeenCalled()
  })

  it('should successfully download the CSV details for this invoice only', async () => {
    const user = userEvent.setup()

    vi.mocked(api.getReimbursementsCsvV2).mockResolvedValueOnce(
      'csv-blob' as never
    )

    render(<InvoiceActions invoice={mockInvoice} />)

    const triggerButton = screen.getByRole('button', { name: 'Télécharger' })
    await user.click(triggerButton)

    const csvMenuItem = screen.getByRole('menuitem', {
      name: DOWNLOAD_REIMBURSEMENTS_LABEL,
    })
    await user.click(csvMenuItem)

    await waitFor(() => {
      expect(api.getReimbursementsCsvV2).toHaveBeenCalledWith({
        query: { invoicesReferences: [mockInvoice.reference] },
        parseAs: 'blob',
      })
    })
    expect(downloadFileModule.downloadFile).toHaveBeenCalledWith(
      'csv-blob',
      'remboursements_pass_culture.csv'
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_INVOICES_DOWNLOAD,
      {
        fileType: 'details',
        filesCount: 1,
        buttonType: 'unique',
      }
    )
    expect(snackBarError).not.toHaveBeenCalled()
  })
})
