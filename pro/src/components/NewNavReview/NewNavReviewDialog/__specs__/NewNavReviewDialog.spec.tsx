import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import NewNavReviewDialog from '../NewNavReviewDialog'

const mockSetIsReviewDialogOpen = vi.fn()

const renderNewNavReviewDialog = () => {
  const storeOverrides = {
    user: {
      selectedOffererId: 1,
    },
  }
  return renderWithProviders(
    <NewNavReviewDialog setIsReviewDialogOpen={mockSetIsReviewDialogOpen} />,
    { storeOverrides }
  )
}

describe('NewNavReviewDialog', () => {
  it('should close dialog on cancel button click', async () => {
    renderNewNavReviewDialog()

    const cancelButton = screen.getByRole('button', { name: 'Annuler' })
    await userEvent.click(cancelButton)

    expect(mockSetIsReviewDialogOpen).toHaveBeenCalledWith(false)
  })

  it('should disable submit button when no options selected', () => {
    renderNewNavReviewDialog()

    const submitButton = screen.getByRole('button', { name: 'Envoyer' })

    expect(submitButton).toBeDisabled()
  })

  it('should close dialog when submit is clicked', async () => {
    vi.spyOn(api, 'submitNewNavReview').mockResolvedValue()
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
    expect(mockSetIsReviewDialogOpen).toHaveBeenCalledWith(false)
  })
})
