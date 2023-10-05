import { render, screen } from '@testing-library/react'
import React from 'react'

import { NoResultsPage } from '../NoResultsPage'

describe('NoResultPage', () => {
  it('should display the searched query when something was searched ', async () => {
    render(<NoResultsPage query="Musée du Louvre" />)

    expect(screen.getByText('Musée du Louvre')).toBeInTheDocument()
  })

  it('should display the default message when nothing was searched ', async () => {
    render(<NoResultsPage query="" />)

    expect(
      screen.getByText(
        'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
      )
    ).toBeInTheDocument()
  })
})
