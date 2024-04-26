import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import NewNavReview from '../NewNavReview'

const renderNewNavReview = () => renderWithProviders(<NewNavReview />)

describe('NewNavReview', () => {
  it('should render review dialog when clicking on the review button', async () => {
    renderNewNavReview()
    await userEvent.click(
      screen.getByRole('button', { name: 'Je donne mon avis' })
    )
    expect(
      screen.getByRole('heading', { name: 'Votre avis compte !' })
    ).toBeInTheDocument()
  })
})
