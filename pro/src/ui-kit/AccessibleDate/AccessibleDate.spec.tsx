import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { AccessibleDate } from './AccessibleDate'

describe('AccessibleDate', () => {
  it('should display date', () => {
    render(<AccessibleDate date="2025-11-12T13:43:59.263Z" />)

    expect(screen.getByText('12/11/2025')).toBeInTheDocument()
    expect(screen.getByText('12 novembre 2025')).toBeInTheDocument()
  })
  it('renders component successfully without accessibility violations', async () => {
    const { container } = render(
      <AccessibleDate date={new Date().toDateString()} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
