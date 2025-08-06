import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import strokeAccessibilityLeg from '@/icons/stroke-accessibility-leg.svg'

import {
  ExternalAccessibilityCollapse,
  ExternalAccessibilityCollapseProps,
} from './ExternalAccessibilityCollapse'

const renderExternalAccessibilityCollaspse = (
  props: Partial<ExternalAccessibilityCollapseProps> = {}
) => {
  renderWithProviders(
    <ExternalAccessibilityCollapse
      icon={strokeAccessibilityLeg}
      title="Handicap moteur"
      isAccessible
      {...props}
    >
      Content
    </ExternalAccessibilityCollapse>
  )
}

describe('ExternalAccessibilityCollapse', () => {
  it('should open and close', async () => {
    renderExternalAccessibilityCollaspse()

    expect(screen.getByText('Handicap moteur')).toBeInTheDocument()
    expect(screen.queryByText('Content')).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByLabelText('Voir les détails pour Handicap moteur')
    )
    expect(screen.queryByText('Content')).toBeInTheDocument()
  })
})
