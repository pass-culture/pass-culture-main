import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Button } from '@/design-system/Button/Button'

import { Card } from './Card'

describe('Card', () => {
  it('should render correctly with no a11y violations', async () => {
    const { container } = render(
      <Card
        imageSrc={'img'}
        title={<h1>My card</h1>}
        actions={<Button label="Action"></Button>}
      >
        Hello
      </Card>
    )
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render content', () => {
    render(
      <Card
        imageSrc={'img'}
        title="My card"
        actions={<Button label="Action"></Button>}
      >
        Hello
      </Card>
    )
    expect(screen.getByText('My card')).toBeInTheDocument()
    expect(screen.getByText('Hello')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })
})
