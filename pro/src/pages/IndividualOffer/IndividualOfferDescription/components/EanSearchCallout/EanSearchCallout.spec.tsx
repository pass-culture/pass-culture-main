import { render, screen } from '@testing-library/react'

import { EanSearchCallout } from './EanSearchCallout'

const renderEanSearchCallout = () => {
  render(<EanSearchCallout />)
}

const LABELS = {
  calloutSuccess: /Ces informations ont été récupérées depuis l’EAN./,
}

describe('EanSearchCallout', () => {
  it('should display a callout with a success message when the offer is still a draft', () => {
    renderEanSearchCallout()
    const callout = screen.getByText(LABELS.calloutSuccess)
    expect(callout).toBeInTheDocument()
  })
})
