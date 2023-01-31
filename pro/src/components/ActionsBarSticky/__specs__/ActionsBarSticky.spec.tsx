import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ActionsBarSticky from '../ActionsBarSticky'

const renderActionsBar = () =>
  renderWithProviders(
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <div>left content</div>
      </ActionsBarSticky.Left>

      <ActionsBarSticky.Right>
        <div>right content</div>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )

describe('ActionsBarSticky', () => {
  it('should render contents', () => {
    renderActionsBar()

    expect(screen.queryByText('left content')).toBeInTheDocument()
    expect(screen.queryByText('right content')).toBeInTheDocument()
  })
})
