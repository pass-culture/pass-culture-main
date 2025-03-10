import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { Button } from 'ui-kit/Button/Button'

import { Tooltip } from './Tooltip'

function renderTooltip() {
  render(
    <Tooltip content="Tooltip content">
      <Button>Tooltip trigger</Button>
    </Tooltip>
  )
}

describe('Tooltip', () => {
  it('should render the tooltip trigger and content', () => {
    renderTooltip()

    expect(screen.getByText('Tooltip trigger')).toBeInTheDocument()
    expect(screen.getByText('Tooltip content')).toBeInTheDocument()
  })

  it('should hide the tooltip content until the trigger is focused', async () => {
    renderTooltip()

    expect(screen.getByText('Tooltip content').parentElement).toHaveClass(
      'visually-hidden'
    )

    await userEvent.click(screen.getByText('Tooltip trigger'))

    expect(screen.getByText('Tooltip content').parentElement).not.toHaveClass(
      'visually-hidden'
    )
  })

  it.skip('should prevent creation a tooltip on a non-interactive trigger', () => {
    try {
      render(
        <Tooltip content="Tooltip content">
          <span>Tooltip content</span>
        </Tooltip>
      )
      expect(true).toBe(false)
    } catch (e: unknown) {
      expect(e).toContain(
        'The tooltip immediate child must be an interactive element of one of the following types'
      )
    }
  })
})
