import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { InfoPanel } from './InfoPanel'
import { InfoPanelSize, InfoPanelSurface } from './types'

describe('<InfoPanel />', () => {
  describe('when surface is FLAT', () => {
    it('should render without accessibility violations', async () => {
      const { container } = render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Panel title"
        >
          Panel content
        </InfoPanel>
      )

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should render the title and the content', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Panel title"
        >
          Panel content
        </InfoPanel>
      )

      expect(
        screen.getByRole('heading', { level: 3, name: 'Panel title' })
      ).toBeInTheDocument()
      expect(screen.getByText('Panel content')).toBeVisible()
    })

    it('should render the icon with an accessible label', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Panel title"
        >
          Panel content
        </InfoPanel>
      )

      expect(screen.getByRole('img', { name: 'Test icon' })).toBeVisible()
    })

    it('should not render a step number', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Panel title"
        >
          Panel content
        </InfoPanel>
      )

      expect(screen.queryByText(/^\d+$/)).not.toBeInTheDocument()
    })

    it('should render JSX children', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Panel title"
        >
          <span data-testid="jsx-child">Rich content</span>
        </InfoPanel>
      )

      expect(screen.getByTestId('jsx-child')).toBeVisible()
      expect(screen.getByText('Rich content')).toBeVisible()
    })
  })

  describe('when surface is ELEVATED', () => {
    it('should render without accessibility violations', async () => {
      const { container } = render(
        <InfoPanel
          surface={InfoPanelSurface.ELEVATED}
          stepNumber={1}
          title="Step one"
        >
          Step description
        </InfoPanel>
      )

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should render the title and the content', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.ELEVATED}
          stepNumber={1}
          title="Step one"
        >
          Step description
        </InfoPanel>
      )

      expect(
        screen.getByRole('heading', { level: 3, name: 'Step one' })
      ).toBeVisible()
      expect(screen.getByText('Step description')).toBeVisible()
    })

    it('should not render an icon', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.ELEVATED}
          stepNumber={1}
          title="Step one"
        >
          Step description
        </InfoPanel>
      )

      expect(screen.queryByRole('img')).not.toBeInTheDocument()
    })

    it('should render JSX children', () => {
      render(
        <InfoPanel
          surface={InfoPanelSurface.ELEVATED}
          stepNumber={1}
          title="Step one"
        >
          <a href="/link">Click here</a>
        </InfoPanel>
      )

      expect(screen.getByRole('link', { name: 'Click here' })).toBeVisible()
    })
  })

  describe('size prop', () => {
    it('should default to large size', () => {
      const { container } = render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Title"
        >
          Content
        </InfoPanel>
      )

      const section = container.querySelector('section') as HTMLElement
      expect(section.className).toContain('large')
      expect(section.className).not.toContain('small')
    })

    it('should apply small size when specified', () => {
      const { container } = render(
        <InfoPanel
          surface={InfoPanelSurface.FLAT}
          icon="/icons/test.svg"
          iconAlt="Test icon"
          title="Title"
          size={InfoPanelSize.SMALL}
        >
          Content
        </InfoPanel>
      )

      const section = container.querySelector('section') as HTMLElement
      expect(section.className).toContain('small')
      expect(section.className).not.toContain('large')
    })
  })
})
