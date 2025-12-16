import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import * as analyticsHook from '@/app/App/analytics/firebase'
import * as useSnackBar from '@/commons/hooks/useSnackBar'

import {
  InvoiceDownloadActionsButton,
  MAX_ITEMS_DOWNLOAD,
} from './InvoiceDownloadActionsButton'

vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: vi.fn(),
}))

vi.mock('@/commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
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

describe('InvoiceDownloadActionsButton', () => {
  it('should show error when downloading more than MAX_ITEMS_DOWNLOAD invoices for justificatifs', async () => {
    const user = userEvent.setup()
    const manyInvoices = Array.from(
      { length: MAX_ITEMS_DOWNLOAD + 1 },
      (_, i) => `INV-${i + 1}`
    )

    render(<InvoiceDownloadActionsButton checkedInvoices={manyInvoices} />)

    await user.click(screen.getByText('Télécharger les justificatifs'))

    expect(snackBarError).toHaveBeenCalledWith(
      `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
    )
  })

  it('should show error when downloading more than MAX_ITEMS_DOWNLOAD invoices for details', async () => {
    const user = userEvent.setup()
    const manyInvoices = Array.from(
      { length: MAX_ITEMS_DOWNLOAD + 1 },
      (_, i) => `INV-${i + 1}`
    )

    render(<InvoiceDownloadActionsButton checkedInvoices={manyInvoices} />)

    await user.click(screen.getByText('Télécharger les détails'))

    expect(snackBarError).toHaveBeenCalledWith(
      `Vous ne pouvez pas télécharger plus de ${MAX_ITEMS_DOWNLOAD} documents en une fois.`
    )
  })
})
