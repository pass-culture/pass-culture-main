import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import ActionsBarPortal from '../ActionsBarPortal'

const renderActionsBar = props => {
  render(
    <ActionsBarPortal {...props}>
      <div>actionsBar content</div>
    </ActionsBarPortal>
  )
}

describe('src | components | layout | ActionsBar', () => {
  it('should not be visible by default', () => {
    renderActionsBar({})

    expect(screen.getByTestId('actions-bar')).not.toHaveClass(
      'actions-bar-visible'
    )
  })

  it('should be visible if isVisible is True', () => {
    renderActionsBar({ isVisible: true })

    expect(screen.getByTestId('actions-bar')).toHaveClass('actions-bar-visible')
  })
})
