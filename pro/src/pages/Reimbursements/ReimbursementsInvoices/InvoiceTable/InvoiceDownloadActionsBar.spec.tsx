import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as analyticsHook from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { downloadFile } from '@/commons/utils/downloadFile'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  InvoiceDownloadActionsBar,
  MAX_ITEMS_DOWNLOAD,
} from './InvoiceDownloadActionsBar'

vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: vi.fn(),
}))

vi.mock('@/commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    getReimbursementsCsvV2: vi.fn(),
    getCombinedInvoices: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const mockLogEvent = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()

  vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
    success: vi.fn(),
    error: snackBarError,
  }))

  vi.spyOn(analyticsHook, 'useAnalytics').mockReturnValue({
    logEvent: mockLogEvent,
  })
})

describe('InvoiceDownloadActionsBar', () => {
  it('should not render the actions bar when no invoice is checked', () => {
    renderWithProviders(<InvoiceDownloadActionsBar checkedInvoices={[]} />)

    expect(
      screen.queryByText('Télécharger les justificatifs (.pdf)')
    ).not.toBeInTheDocument()
  })

  it('should display the count with a singular label when only one invoice is checked', () => {
    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1']} />
    )

    expect(screen.getByText('1 justificatif sélectionné')).toBeInTheDocument()
  })

  it('should display the count with a plural label when several invoices are checked', () => {
    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1', 'INV-2']} />
    )

    expect(screen.getByText('2 justificatifs sélectionnés')).toBeInTheDocument()
  })

  it('should download the PDF justificatifs and log the event on success', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getCombinedInvoices).mockResolvedValueOnce(
      'pdf-blob' as never
    )

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1', 'INV-2']} />
    )

    await user.click(screen.getByText('Télécharger les justificatifs (.pdf)'))

    expect(api.getCombinedInvoices).toHaveBeenCalledWith({
      query: { invoiceReferences: ['INV-1', 'INV-2'] },
    })
    expect(downloadFile).toHaveBeenCalledWith(
      'pdf-blob',
      'justificatif_remboursement_pass_culture.pdf'
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_INVOICES_DOWNLOAD,
      {
        fileType: 'justificatif',
        filesCount: 2,
        buttonType: 'multiple',
      }
    )
    expect(snackBarError).not.toHaveBeenCalled()
  })

  it('should show a generic error when downloading the PDF justificatifs fails', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getCombinedInvoices).mockRejectedValueOnce(new Error('boom'))

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1']} />
    )

    await user.click(screen.getByText('Télécharger les justificatifs (.pdf)'))

    expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    expect(downloadFile).not.toHaveBeenCalled()
  })

  it('should show error when downloading more than MAX_ITEMS_DOWNLOAD invoices for justificatifs', async () => {
    const user = userEvent.setup()
    const manyInvoices = Array.from(
      { length: MAX_ITEMS_DOWNLOAD + 1 },
      (_, i) => `INV-${i + 1}`
    )

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={manyInvoices} />
    )

    await user.click(screen.getByText('Télécharger les justificatifs (.pdf)'))

    expect(snackBarError).toHaveBeenCalledWith(
      `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
    )
  })

  it('should download the CSV details and log the event on success', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getReimbursementsCsvV2).mockResolvedValueOnce(
      'csv-blob' as never
    )

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1', 'INV-2']} />
    )

    await user.click(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    )

    expect(api.getReimbursementsCsvV2).toHaveBeenCalledWith({
      query: { invoicesReferences: ['INV-1', 'INV-2'] },
      parseAs: 'blob',
    })
    expect(downloadFile).toHaveBeenCalledWith(
      'csv-blob',
      'remboursements_pass_culture.csv'
    )
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_INVOICES_DOWNLOAD,
      {
        fileType: 'details',
        filesCount: 2,
        buttonType: 'multiple',
      }
    )
    expect(snackBarError).not.toHaveBeenCalled()
  })

  it('should show a generic error when downloading the CSV details fails', async () => {
    const user = userEvent.setup()
    vi.mocked(api.getReimbursementsCsvV2).mockRejectedValueOnce(
      new Error('boom')
    )

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={['INV-1']} />
    )

    await user.click(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    )

    expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    expect(downloadFile).not.toHaveBeenCalled()
  })

  it('should show error when downloading more than MAX_ITEMS_DOWNLOAD invoices for details', async () => {
    const user = userEvent.setup()
    const manyInvoices = Array.from(
      { length: MAX_ITEMS_DOWNLOAD + 1 },
      (_, i) => `INV-${i + 1}`
    )

    renderWithProviders(
      <InvoiceDownloadActionsBar checkedInvoices={manyInvoices} />
    )

    await user.click(
      screen.getByText('Télécharger le détail des réservations (.csv)')
    )

    expect(snackBarError).toHaveBeenCalledWith(
      `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
    )
  })
})
