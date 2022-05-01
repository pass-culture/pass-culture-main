import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithStyles } from 'utils/testHelpers'

import ActionsBarPortal from '../ActionsBarPortal'

const renderActionsBar = props => {
  return renderWithStyles(
    <ActionsBarPortal {...props}>
      <div>actionsBar content</div>
    </ActionsBarPortal>,
    {
      stylesheet: 'components/layout/ActionsBarPortal/_ActionsBarPortal',
    }
  )
}

describe('src | components | layout | ActionsBar', () => {
  it.skip('should not be visible by default', () => {
    renderActionsBar({})

    expect(screen.getByText('actionsBar content')).not.toBeVisible()
  })

  it.skip('should be visible if isVisible is True', async () => {
    renderActionsBar({ isVisible: true })

    expect(screen.getByText('actionsBar content')).toBeVisible()
  })
})
