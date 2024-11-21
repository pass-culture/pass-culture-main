import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useNotification from 'commons/hooks/useNotification'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { UserReviewDialog } from 'components/UserReview/UserReviewDialog/UserReviewDialog'

const notifyError = vi.fn()

const renderUserReviewDialog = () => {
  const storeOverrides = {
    user: {
      selectedOffererId: 1,
      currentUser: sharedCurrentUserFactory(),
    },
  }
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <UserReviewDialog />
      </Dialog.Content>
    </Dialog.Root>,
    { storeOverrides }
  )
}

describe('UserReviewDialog', () => {
  it('should close dialog on cancel button click', async () => {
    renderUserReviewDialog()

    const cancelButton = screen.getByRole('button', { name: 'Annuler' })
    await userEvent.click(cancelButton)

    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should disable submit button when no options selected', () => {
    renderUserReviewDialog()

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    expect(submitButton).toBeDisabled()
  })

  it('should submit data when submit button is clicked', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(
      screen.getByLabelText(
        'Souhaitez-vous préciser ? Nous lisons tous les commentaires. 🙂'
      ),
      'Commentaire utilisateur'
    )

    await userEvent.click(submitButton)

    expect(api.submitUserReview).toHaveBeenCalledWith({
      userSatisfaction: 'Excellente',
      userComment: 'Commentaire utilisateur',
      location: location.pathname,
      offererId: 1,
    })
  })

  it('should show confirmation dialog when submitting data', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    await userEvent.click(submitButton)
    expect(
      screen.getByText('Merci beaucoup de votre participation !')
    ).toBeInTheDocument()
  })

  it('should close confirmation dialog when close button is clicked', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)
    await userEvent.click(screen.getByRole('button', { name: 'Fermer' }))
    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should show error message and close dialog on error', async () => {
    vi.spyOn(api, 'submitUserReview').mockRejectedValueOnce(new Error())

    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue. Merci de réessayer plus tard.'
    )
  })
})
