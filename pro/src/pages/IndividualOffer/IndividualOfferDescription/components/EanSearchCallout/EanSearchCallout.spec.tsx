import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { EanSearchCallout } from './EanSearchCallout'

const renderEanSearchCallout = () => {
  return render(<EanSearchCallout />)
}

const LABELS = {
  calloutSuccess: /Ces informations ont été récupérées depuis l’EAN./,
}

describe('EanSearchCallout', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderEanSearchCallout()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a callout with a success message when the offer is still a draft', () => {
    renderEanSearchCallout()
    const callout = screen.getByText(LABELS.calloutSuccess)
    expect(callout).toBeInTheDocument()
  })
})
