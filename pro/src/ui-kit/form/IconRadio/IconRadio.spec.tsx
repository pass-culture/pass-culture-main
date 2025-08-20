import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { IconRadio } from './IconRadio'

describe('IconRadio', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <IconRadio label="Radio 1" icon="A" name="myField" />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a radio input', () => {
    render(<IconRadio label="Radio 1" icon="A" name="myField" />)

    expect(screen.getByLabelText('Radio 1')).toBeInTheDocument()
  })
})
