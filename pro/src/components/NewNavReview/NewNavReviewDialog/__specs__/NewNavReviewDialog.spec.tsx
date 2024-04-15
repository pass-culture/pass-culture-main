import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'utils/renderWithProviders'

import NewNavReviewDialog from '../NewNavReviewDialog'

const mockSetIsReviewDialogOpen = vi.fn()

const renderNewNavReviewDialog = () => {
  return renderWithProviders(
    <NewNavReviewDialog setIsReviewDialogOpen={mockSetIsReviewDialogOpen} />
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

    expect(mockSetIsReviewDialogOpen).toHaveBeenCalledWith(false)
  })
})
