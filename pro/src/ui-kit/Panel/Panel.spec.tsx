import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Panel } from './Panel'

describe('components:Panel', () => {
  it('renders component successfully without accessibility violations', async () => {
    const { container } = render(<Panel>I’m a test</Panel>)
    expect(screen.getByText('I’m a test')).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })
})
