import { render, screen } from '@testing-library/react'

import { Component as VenueManagement } from './VenueManagement'

describe('VenueManagement', () => {
  it('should render the banner and the button', () => {
    render(<VenueManagement />)

    expect(screen.getByText('Fermeture de la structure')).toBeVisible()
    expect(
      screen.getByText('Toutes vos offres seront retirées du pass Culture.')
    ).toBeVisible()
    expect(
      screen.getByRole('button', { name: /Fermer la structure/ })
    ).toBeVisible()
  })
})
