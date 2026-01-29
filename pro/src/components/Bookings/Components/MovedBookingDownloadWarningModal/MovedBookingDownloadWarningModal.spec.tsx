import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { MovedBookingDownloadWarningModal } from './MovedBookingDownloadWarningModal'

function renderMovedBookingDownloadWarningModal() {
  return renderWithProviders(<MovedBookingDownloadWarningModal />)
}

describe('MovedBookingDownloadWarningModal', () => {
  it('should render the trigger button with correct label', () => {
    renderMovedBookingDownloadWarningModal()

    expect(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    ).toBeInTheDocument()
  })

  it('should open dialog when clicking the trigger button', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('should display visually hidden title for accessibility', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    const dialog = screen.getByRole('dialog')
    const title = within(dialog).getByRole('heading', {
      name: 'Le téléchargement des réservations a déménagé',
    })
    expect(title).toBeInTheDocument()
  })

  it('should display the catchline and description in dialog', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    expect(screen.getByText('Nouveau !')).toBeInTheDocument()
    expect(
      screen.getByText(/Retrouvez dorénavant tous vos exports de réservations/)
    ).toBeInTheDocument()
  })

  it('should display the header image as decorative', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    const image = document.querySelector('img.header-image')
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('aria-hidden', 'true')
    expect(image).toHaveAttribute('alt', '')
  })

  it('should render link to the download page', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    const link = screen.getByRole('link', {
      name: 'Aller sur la nouvelle page de téléchargement',
    })
    expect(link).toHaveAttribute('href', '/remboursements')
  })

  it('should close dialog when clicking the link button', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    expect(screen.getByRole('dialog')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('link', {
        name: 'Aller sur la nouvelle page de téléchargement',
      })
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('should close dialog when clicking the close button', async () => {
    renderMovedBookingDownloadWarningModal()

    await userEvent.click(
      screen.getByRole('button', { name: 'Où les télécharger ?' })
    )

    expect(screen.getByRole('dialog')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})
