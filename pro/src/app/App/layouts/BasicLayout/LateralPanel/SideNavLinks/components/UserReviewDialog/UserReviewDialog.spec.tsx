import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Button } from '@/design-system/Button/Button'

import { UserReviewDialog } from './UserReviewDialog'

const snackBarError = vi.fn()

type RenderOptions = {
  isAdminSpace?: boolean
  storeUserOverrides?: Record<string, unknown>
}

const renderUserReviewDialog = ({
  isAdminSpace = false,
  storeUserOverrides,
}: RenderOptions = {}) => {
  const storeOverrides = {
    user: {
      currentUser: sharedCurrentUserFactory(),
      selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      ...storeUserOverrides,
    },
  }
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <Dialog.Title>Title</Dialog.Title>
        <UserReviewDialog
          dialogTrigger={<Button label="Trigger"></Button>}
          isAdminSpace={isAdminSpace}
        />
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
      body: {
        userSatisfaction: 'Excellente',
        userComment: 'Commentaire utilisateur',
        pageTitle: '',
        location: location.pathname,
        offererId: 1,
      },
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

  it('should submit with the selected admin offerer id in admin space', async () => {
    vi.spyOn(api, 'submitUserReview').mockResolvedValueOnce()
    renderUserReviewDialog({
      isAdminSpace: true,
      storeUserOverrides: {
        selectedAdminOfferer: { ...defaultGetOffererResponseModel, id: 42 },
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    })

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(screen.getByRole('textbox'), 'description')

    await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

    expect(api.submitUserReview).toHaveBeenCalledWith({
      body: expect.objectContaining({ offererId: 42 }),
    })
  })

  it('should not call submitUserReview when no offerer is selected in admin space', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {})
    const submitSpy = vi.spyOn(api, 'submitUserReview').mockResolvedValue()
    renderUserReviewDialog({
      isAdminSpace: true,
      storeUserOverrides: {
        selectedAdminOfferer: null,
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    })

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    await userEvent.click(screen.getByRole('radio', { name: 'Excellente' }))
    await userEvent.type(screen.getByRole('textbox'), 'description')

    await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

    expect(submitSpy).not.toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        message: '`selectedOffererId` is null.',
      })
    )
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
