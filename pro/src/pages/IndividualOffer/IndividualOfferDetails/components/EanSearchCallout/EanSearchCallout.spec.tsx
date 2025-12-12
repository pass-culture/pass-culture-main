import { render, screen } from '@testing-library/react'

import { EanSearchCallout } from './EanSearchCallout'

const renderEanSearchCallout = (isDraftOffer = false) => {
  render(<EanSearchCallout isDraftOffer={isDraftOffer} />)
}

const LABELS = {
  calloutSuccess: /Ces informations ont été récupérées depuis l’EAN./,
  calloutInfo:
    /Ces informations proviennent de l’EAN et ne peuvent pas être modifiées./,
}

describe('EanSearchCallout', () => {
  it('should display a callout with a success message when the offer is still a draft', () => {
    renderEanSearchCallout(true)
    const callout = screen.getByText(LABELS.calloutSuccess)
    expect(callout).toBeInTheDocument()
  })

  it('should display a callout with an info message when the offer is not a draft', () => {
    renderEanSearchCallout(false)
    const callout = screen.getByText(LABELS.calloutInfo)
    expect(callout).toBeInTheDocument()
  })
})
