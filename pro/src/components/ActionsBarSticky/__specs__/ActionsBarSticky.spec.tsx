import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import ActionsBarSticky from '../ActionsBarSticky'

const renderActionsBar = () => {
  render(
    <Provider store={configureTestStore()}>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <div>left content</div>
        </ActionsBarSticky.Left>

        <ActionsBarSticky.Right>
          <div>right content</div>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </Provider>
  )
}

describe('ActionsBarSticky', () => {
  it('should render contents', () => {
    renderActionsBar()

    expect(screen.queryByText('left content')).toBeInTheDocument()
    expect(screen.queryByText('right content')).toBeInTheDocument()
  })
})
