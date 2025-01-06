import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { UserReview } from '../UserReview'

const renderUserReview = () => renderWithProviders(<UserReview />)

describe('UserReview', () => {
  it('should render review dialog when clicking on the review button', async () => {
    renderUserReview()
    await userEvent.click(
      screen.getByRole('button', { name: 'Je donne mon avis' })
    )
    expect(
      screen.getByRole('heading', { name: 'Votre avis compte !' })
    ).toBeInTheDocument()
  })
})
