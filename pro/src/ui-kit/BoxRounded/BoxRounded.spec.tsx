import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { BoxRounded } from './BoxRounded'

describe('BoxRounded', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(<BoxRounded>Content</BoxRounded>)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the box with a footer', () => {
    render(
      <BoxRounded onClickModify={() => {}} footer={<>Footer</>}>
        Content
      </BoxRounded>
    )

    expect(screen.getByText('Footer')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should display the box without the edit button if there is no callback', () => {
    render(<BoxRounded>Content</BoxRounded>)

    expect(
      screen.queryByRole('button', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })
})
