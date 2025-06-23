import { render, screen } from '@testing-library/react'

import { EanSearchCallout } from './EanSearchCallout'

const renderEanSearchCallout = (isDraftOffer = false) => {
  render(<EanSearchCallout isDraftOffer={isDraftOffer} />)
}

const LABELS = {
  calloutSuccess: /Les informations suivantes ont été synchronisées/,
  calloutInfo: /Les informations de cette page ne sont pas modifiables/,
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
