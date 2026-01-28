import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Button } from '@/design-system/Button/Button'

import { UserReviewDialog } from './UserReviewDialog'

const snackBarError = vi.fn()

const renderUserReviewDialog = () => {
  const storeOverrides = {
    user: {
      currentUser: sharedCurrentUserFactory(),
    },
    offerer: currentOffererFactory(),
  }
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <Dialog.Title>Title</Dialog.Title>
        <UserReviewDialog dialogTrigger={<Button label="Trigger"></Button>} />
      </Dialog.Content>
    </Dialog.Root>,
    { storeOverrides }
  )
}

describe('UserReviewDialog', () => {
  it('should close dialog on cancel button click', async () => {
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    const cancelButton = screen.getByRole('button', { name: 'Annuler' })
    await userEvent.click(cancelButton)

    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should submit data when submit button is clicked', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.type(screen.getByRole('textbox'), 'Commentaire utilisateur')

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))

    await userEvent.click(submitButton)

    expect(api.submitUserReview).toHaveBeenCalledWith({
      userSatisfaction: 'Excellente',
      userComment: 'Commentaire utilisateur',
      pageTitle: '',
      location: location.pathname,
      offererId: 1,
    })
  })

  it('should show confirmation dialog when submitting data', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(screen.getByRole('textbox'), 'description')

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    await userEvent.click(submitButton)
    expect(
      screen.getByText('Merci beaucoup de votre participation !')
    ).toBeInTheDocument()
  })

  it('should close confirmation dialog when close button is clicked', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(screen.getByRole('textbox'), 'description')

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)
    await userEvent.click(screen.getByRole('button', { name: 'Fermer' }))
    expect(
      screen.queryByRole('heading', { name: 'Votre avis compte !' })
    ).not.toBeInTheDocument()
  })

  it('should show error message and close dialog on error', async () => {
    vi.spyOn(api, 'submitUserReview').mockRejectedValueOnce(new Error())

    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))

    renderUserReviewDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(screen.getByRole('textbox'), 'description')

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })
    await userEvent.click(submitButton)

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue. Merci de réessayer plus tard.'
    )
  })
})
