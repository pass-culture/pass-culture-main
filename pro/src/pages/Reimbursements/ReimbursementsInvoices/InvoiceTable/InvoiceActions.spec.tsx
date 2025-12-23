import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import type { InvoiceResponseV2Model } from '@/apiClient/v1'
import * as analyticsHook from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import * as downloadFileModule from '@/commons/utils/downloadFile'

import { InvoiceActions } from './InvoiceActions'

vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: vi.fn(),
}))

vi.mock('@/commons/utils/downloadFile', () => ({
  downloadFile: vi.fn(),
}))

const snackBarError = vi.fn()
const mockLogEvent = vi.fn()

const mockInvoice: InvoiceResponseV2Model = {
  reference: 'INV-001',
  date: '2024-06-01',
  amount: 150,
  bankAccountLabel: 'Bank A',
  cashflowLabels: ['VIRE-001'],
  url: 'https://example.com/invoice.pdf',
}

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

describe('InvoiceActions', () => {
  it('should display error message when PDF download fails', async () => {
    const user = userEvent.setup()

    // Mock fetch to fail
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'))

    render(<InvoiceActions invoice={mockInvoice} />)

    // Open the dropdown menu
    const triggerButton = screen.getByRole('button', {
      name: 'Téléchargement des justificatifs',
    })
    await user.click(triggerButton)

    // Click on the PDF download menu item
    const pdfDownloadMenuItem = screen.getByRole('menuitem', {
      name: 'Télécharger le justificatif comptable (.pdf)',
    })
    await user.click(pdfDownloadMenuItem)

    // Wait for the error to be called
    await waitFor(() => {
      expect(snackBarError).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
    })

    // Verify that downloadFile was not called (since fetch failed)
    expect(downloadFileModule.downloadFile).not.toHaveBeenCalled()
  })

  it('should successfully download PDF when fetch succeeds', async () => {
    const user = userEvent.setup()

    // Mock fetch to succeed
    const mockBlob = new Blob(['dummy-pdf-content'], {
      type: 'application/pdf',
    })
    global.fetch = vi.fn().mockResolvedValueOnce({
      blob: () => Promise.resolve(mockBlob),
    } as Response)

    render(<InvoiceActions invoice={mockInvoice} />)

    // Open the dropdown menu
    const triggerButton = screen.getByRole('button', {
      name: 'Téléchargement des justificatifs',
    })
    await user.click(triggerButton)

    // Click on the PDF download menu item
    const pdfDownloadMenuItem = screen.getByRole('menuitem', {
      name: 'Télécharger le justificatif comptable (.pdf)',
    })
    await user.click(pdfDownloadMenuItem)

    // Wait for the download to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(mockInvoice.url)
      expect(downloadFileModule.downloadFile).toHaveBeenCalledWith(
        mockBlob,
        'justificatif_comptable.pdf'
      )
    })

    // Verify analytics event was logged
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_INVOICES_DOWNLOAD,
      {
        fileType: 'justificatif',
        filesCount: 1,
        buttonType: 'unique',
      }
    )

    // Verify no error was shown
    expect(snackBarError).not.toHaveBeenCalled()
  })
})
