import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { NewNavReviewDialog } from '../NewNavReviewDialog'

const notifyError = vi.fn()

const renderNewNavReviewDialog = () => {
  const storeOverrides = {
    user: {
      selectedOffererId: 1,
      currentUser: sharedCurrentUserFactory(),
    },
  }
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <NewNavReviewDialog />
      </Dialog.Content>
    </Dialog.Root>,
    { storeOverrides }
  )
}

describe('NewNavReviewDialog', () => {
  it('should close dialog on cancel button click', async () => {
    renderNewNavReviewDialog()

    const cancelButton = screen.getByRole('button', { name: 'Annuler' })
    await userEvent.click(cancelButton)

    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should disable submit button when no options selected', () => {
    renderNewNavReviewDialog()

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    expect(submitButton).toBeDisabled()
  })

  it('should submit data when submit button is clicked', async () => {
    vi.spyOn(api, 'submitNewNavReview').mockResolvedValueOnce()
    renderNewNavReviewDialog()

    const morePleasantRadioButton = screen.getByRole('radio', {
      name: /Plus agréable/,
    })
    await userEvent.click(morePleasantRadioButton)
    const moreConvenientRadioButton = screen.getByRole('radio', {
      name: /Plus pratique/,
    })
    await userEvent.click(moreConvenientRadioButton)

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.type(
      screen.getByLabelText(
        'Souhaitez-vous préciser ? Nous lisons tous les commentaires. 🙂'
      ),
      'Commentaire utilisateur'
    )

    await userEvent.click(submitButton)

    expect(api.submitNewNavReview).toHaveBeenCalledWith({
      isPleasant: true,
      isConvenient: true,
      comment: 'Commentaire utilisateur',
      location: location.pathname,
      offererId: 1,
    })
  })

  it('should show confirmation dialog when submitting data', async () => {
    vi.spyOn(api, 'submitNewNavReview').mockResolvedValueOnce()
    renderNewNavReviewDialog()

    const morePleasantRadioButton = screen.getByRole('radio', {
      name: /Plus agréable/,
    })
    await userEvent.click(morePleasantRadioButton)
    const moreConvenientRadioButton = screen.getByRole('radio', {
      name: /Plus pratique/,
    })
    await userEvent.click(moreConvenientRadioButton)

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    await userEvent.click(submitButton)
    expect(
      screen.getByText('Merci beaucoup de votre participation !')
    ).toBeInTheDocument()
  })

  it('should close confirmation dialog when close button is clicked', async () => {
    vi.spyOn(api, 'submitNewNavReview').mockResolvedValueOnce()
    renderNewNavReviewDialog()

    const morePleasantRadioButton = screen.getByRole('radio', {
      name: /Plus agréable/,
    })
    await userEvent.click(morePleasantRadioButton)
    const moreConvenientRadioButton = screen.getByRole('radio', {
      name: /Plus pratique/,
    })
    await userEvent.click(moreConvenientRadioButton)

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)
    await userEvent.click(screen.getByRole('button', { name: 'Fermer' }))
    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should show error message and close dialog on error', async () => {
    vi.spyOn(api, 'submitNewNavReview').mockRejectedValueOnce(new Error())

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    renderNewNavReviewDialog()

    const morePleasantRadioButton = screen.getByRole('radio', {
      name: /Plus agréable/,
    })
    await userEvent.click(morePleasantRadioButton)
    const moreConvenientRadioButton = screen.getByRole('radio', {
      name: /Plus pratique/,
    })
    await userEvent.click(moreConvenientRadioButton)

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue. Merci de réessayer plus tard.'
    )
  })
})
