import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { axe } from 'vitest-axe'

import fullLinkIcon from '@/icons/full-link.svg'

import { Link } from './Link'
import { LinkColor, type LinkProps, LinkSize } from './types'

function renderLink(props: Partial<LinkProps> = {}) {
  const { label = 'Label', to = '/somewhere', ...rest } = props

  return render(
    <MemoryRouter>
      <Link label={label} to={to} {...rest} />
    </MemoryRouter>
  )
}

describe('Link', () => {
  it('should render without accessibility violations (internal)', async () => {
    const { container } = renderLink()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render without accessibility violations (external)', async () => {
    const { container } = renderLink({
      isExternalLink: true,
      to: 'https://example.com',
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the label', () => {
    renderLink()

    expect(screen.getByRole('link', { name: 'Label' })).toBeInTheDocument()
  })

  describe('Sizes', () => {
    it('should render DEFAULT size by default', () => {
      renderLink()

      expect(screen.getByRole('link')).toHaveClass('link-default')
    })

    it.each([
      [LinkSize.DEFAULT, 'link-default'],
      [LinkSize.SMALL, 'link-small'],
      [LinkSize.EXTRA_SMALL, 'link-extra-small'],
    ])('should apply class for size %s', (size, expectedClass) => {
      renderLink({ size })

      expect(screen.getByRole('link')).toHaveClass(expectedClass)
    })
  })

  describe('Colors', () => {
    it('should render BRAND color by default', () => {
      renderLink()

      expect(screen.getByRole('link')).toHaveClass('link-brand')
    })

    it.each([
      [LinkColor.BRAND, 'link-brand'],
      [LinkColor.NEUTRAL, 'link-neutral'],
    ])('should apply class for color %s', (color, expectedClass) => {
      renderLink({ color })

      expect(screen.getByRole('link')).toHaveClass(expectedClass)
    })
  })

  describe('Internal link rendering', () => {
    it('should render a router link', () => {
      renderLink()

      const link = screen.getByRole('link', { name: /Label/ })
      expect(link).toHaveAttribute('href', '/somewhere')
    })

    it('should not render an icon by default', () => {
      const { container } = renderLink()

      expect(container.querySelector('svg')).not.toBeInTheDocument()
    })

    it('should render an icon when icon is provided', () => {
      const { container } = renderLink({ icon: fullLinkIcon })

      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should render an icon when shouldOpenNewTab is true', () => {
      const { container } = renderLink({ shouldOpenNewTab: true })

      expect(container.querySelector('svg')).toBeInTheDocument()
      expect(
        screen.getByRole('img', { name: 'Nouvelle fenêtre' })
      ).toBeInTheDocument()
      expect(screen.getByRole('link')).toHaveAttribute('target', '_blank')
    })

    it('should add icon alt when shouldOpenNewTab is true', () => {
      renderLink({ shouldOpenNewTab: true })

      expect(
        screen.getByRole('img', { name: 'Nouvelle fenêtre' })
      ).toBeInTheDocument()
    })

    it('should open in new tab when shouldOpenNewTab is true', () => {
      renderLink({ shouldOpenNewTab: true })

      expect(screen.getByRole('link')).toHaveAttribute('target', '_blank')
    })

    it('should call onClick', async () => {
      const handleClick = vi.fn()
      renderLink({ onClick: handleClick })

      await userEvent.click(screen.getByRole('link', { name: /Label/ }))

      expect(handleClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('External rendering', () => {
    it('should render a native anchor with the given href', () => {
      renderLink({ isExternalLink: true, to: 'https://example.com' })

      const link = screen.getByRole('link', { name: /Label/ })
      expect(link).toHaveAttribute('href', 'https://example.com')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should render an icon when icon is provided', () => {
      const { container } = renderLink({
        isExternalLink: true,
        to: 'https://example.com',
        icon: fullLinkIcon,
      })

      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should add icon when shouldOpenNewTab is true', () => {
      const { container } = renderLink({
        isExternalLink: true,
        to: 'https://example.com',
        shouldOpenNewTab: true,
      })

      expect(container.querySelector('svg')).toBeInTheDocument()
    })

    it('should open in new tab when shouldOpenNewTab is true', () => {
      renderLink({
        isExternalLink: true,
        to: 'https://example.com',
        shouldOpenNewTab: true,
      })

      expect(screen.getByRole('link')).toHaveAttribute('target', '_blank')
    })

    it('should add icon alt when shouldOpenNewTab is true', () => {
      renderLink({
        isExternalLink: true,
        to: 'https://example.com',
        shouldOpenNewTab: true,
      })

      expect(
        screen.getByRole('img', { name: 'Nouvelle fenêtre' })
      ).toBeInTheDocument()
    })

    it('should call onClick', async () => {
      const handleClick = vi.fn()
      renderLink({
        isExternalLink: true,
        to: 'https://example.com',
        onClick: handleClick,
      })

      await userEvent.click(screen.getByRole('link', { name: /Label/ }))

      expect(handleClick).toHaveBeenCalledTimes(1)
    })
  })
})
