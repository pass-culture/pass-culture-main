import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import strokeAccessibilityLeg from 'icons/stroke-accessibility-leg.svg'

import {
  AccesLibreCollapse,
  AccesLibreCollapseProps,
} from '../AccesLibreCollapse'

const renderAccesLibreCollapse = (
  props: Partial<AccesLibreCollapseProps> = {}
) => {
  renderWithProviders(
    <AccesLibreCollapse
      icon={strokeAccessibilityLeg}
      title="Handicap moteur"
      isAccessible
      {...props}
    >
      Content
    </AccesLibreCollapse>
  )
}

describe('AccesLibreCollapse', () => {
  it('should open and close', async () => {
    renderAccesLibreCollapse()

    expect(screen.getByText('Handicap moteur')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeVisible()

    await userEvent.click(
      screen.getByLabelText('Voir les détails pour Handicap moteur')
    )
    expect(screen.queryByText('Content')).not.toBeInTheDocument()
  })
})
