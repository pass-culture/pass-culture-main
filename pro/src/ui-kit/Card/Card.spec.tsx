import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { Button } from '@/design-system/Button/Button'

import { Card } from './Card'

describe('Card', () => {
  describe('Accessibility', () => {
    it('should have no a11y violations with complete card', async () => {
      const { container } = render(
        <Card>
          <Card.Header title="My card" subtitle="Subtitle" />
          <Card.Content>Hello</Card.Content>
          <Card.Footer>
            <Button label="Action" />
          </Card.Footer>
        </Card>
      )
      expect(await axe(container)).toHaveNoViolations()
    })

    it('should have no a11y violations with info variant', async () => {
      const { container } = render(
        <Card variant="info">
          <Card.Header title="Info card" subtitle="With colored background" />
          <Card.Content>Info content</Card.Content>
          <Card.Footer>
            <Button label="Learn more" />
          </Card.Footer>
        </Card>
      )
      expect(await axe(container)).toHaveNoViolations()
    })

    it('should have no a11y violations with image', async () => {
      const { container } = render(
        <Card>
          <Card.Image src="/test-image.jpg" alt="Test image description" />
          <Card.Header title="Card with image" />
          <Card.Content>Content</Card.Content>
        </Card>
      )
      expect(await axe(container)).toHaveNoViolations()
    })
  })

  describe('Rendering', () => {
    it('should render header with title and subtitle', () => {
      render(
        <Card>
          <Card.Header title="My card" subtitle="My subtitle" />
        </Card>
      )
      expect(screen.getByText('My card')).toBeVisible()
      expect(screen.getByText('My subtitle')).toBeVisible()
    })

    it('should render content', () => {
      render(
        <Card>
          <Card.Content>Hello World</Card.Content>
        </Card>
      )
      expect(screen.getByText('Hello World')).toBeVisible()
    })

    it('should render footer with actions', () => {
      render(
        <Card>
          <Card.Footer>
            <Button label="Action" />
          </Card.Footer>
        </Card>
      )
      expect(screen.getByText('Action')).toBeVisible()
    })

    it('should render image with alt text', () => {
      render(
        <Card>
          <Card.Image src="/test.jpg" alt="Test image" />
        </Card>
      )
      const image = screen.getByAltText('Test image')
      expect(image).toBeVisible()
      expect(image).toHaveAttribute('src', '/test.jpg')
    })
  })

  describe('Variants', () => {
    it('should render with info variant', () => {
      const { container } = render(
        <Card variant="info">
          <Card.Header title="Info card" />
        </Card>
      )
      const cardElement = container.querySelector('.card-info')
      expect(cardElement).toBeVisible()
    })
  })

  describe('Title tags', () => {
    it('should use h2 as default title tag', () => {
      render(
        <Card>
          <Card.Header title="Default heading" />
        </Card>
      )
      const heading = screen.getByText('Default heading')
      expect(heading.tagName).toBe('H2')
    })

    it('should use h3 when specified', () => {
      render(
        <Card>
          <Card.Header title="Custom heading" titleTag="h3" />
        </Card>
      )
      const heading = screen.getByText('Custom heading')
      expect(heading.tagName).toBe('H3')
    })
  })
})
