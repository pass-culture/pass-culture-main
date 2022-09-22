import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import ActionsBarSticky, { IActionsBarStickyProps } from '../ActionsBarSticky'

const renderActionsBar = (props: IActionsBarStickyProps) => {
  render(
    <ActionsBarSticky
      {...props}
      left={<div>left content</div>}
      right={<div>right content</div>}
    />
  )
}

describe('ActionsBarSticky', () => {
  it('should not be visible by default', () => {
    renderActionsBar({})

    expect(screen.queryByText('actionsBar content')).not.toBeInTheDocument()
  })

  it('should be visible if isVisible is True', () => {
    renderActionsBar({ isVisible: true })

    expect(screen.queryByText('left content')).toBeInTheDocument()
    expect(screen.queryByText('right content')).toBeInTheDocument()
  })
})
