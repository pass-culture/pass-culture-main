import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { axe } from 'vitest-axe'

import fullNextIcon from '@/icons/full-next.svg'

import { Button } from './Button'
import {
  ButtonColor,
  type ButtonProps,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from './types'

const renderButton = (props: ButtonProps) => {
  return render(
    <MemoryRouter>
      <Button {...props} />
    </MemoryRouter>
  )
}

describe('Button', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderButton({
      label: 'Button Label',
      variant: ButtonVariant.PRIMARY,
      size: ButtonSize.DEFAULT,
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render a button with a label', () => {
    renderButton({
      label: 'Button Label',
      variant: ButtonVariant.PRIMARY,
      size: ButtonSize.DEFAULT,
    })

    expect(screen.getByText('Button Label')).toBeInTheDocument()
  })

  describe('Variants', () => {
    it('should render PRIMARY variant', () => {
      renderButton({
        label: 'Primary Button',
        variant: ButtonVariant.PRIMARY,
      })

      const button = screen.getByRole('button', { name: 'Primary Button' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('btn-primary')
    })

    it('should render SECONDARY variant', () => {
      renderButton({
        label: 'Secondary Button',
        variant: ButtonVariant.SECONDARY,
      })

      const button = screen.getByRole('button', { name: 'Secondary Button' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('btn-secondary')
    })

    it('should render TERTIARY variant', () => {
      renderButton({
        label: 'Tertiary Button',
        variant: ButtonVariant.TERTIARY,
      })

      const button = screen.getByRole('button', { name: 'Tertiary Button' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('btn-tertiary')
    })
  })

  describe('Colors', () => {
    it('should render BRAND color by default', () => {
      renderButton({
        label: 'Brand Button',
      })

      const button = screen.getByRole('button', { name: 'Brand Button' })
      expect(button).toHaveClass('btn-brand')
    })

    it('should render BRAND color', () => {
      renderButton({
        label: 'Brand Button',
        color: ButtonColor.BRAND,
      })

      const button = screen.getByRole('button', { name: 'Brand Button' })
      expect(button).toHaveClass('btn-brand')
    })

    it('should render NEUTRAL color', () => {
      renderButton({
        label: 'Neutral Button',
        color: ButtonColor.NEUTRAL,
      })

      const button = screen.getByRole('button', { name: 'Neutral Button' })
      expect(button).toHaveClass('btn-neutral')
    })
  })

  describe('Sizes', () => {
    it('should render DEFAULT size by default', () => {
      renderButton({
        label: 'Default Size Button',
      })

      const button = screen.getByRole('button', { name: 'Default Size Button' })
      expect(button).toHaveClass('btn-default')
    })

    it('should render DEFAULT size', () => {
      renderButton({
        label: 'Default Size Button',
        size: ButtonSize.DEFAULT,
      })

      const button = screen.getByRole('button', { name: 'Default Size Button' })
      expect(button).toHaveClass('btn-default')
    })

    it('should render SMALL size', () => {
      renderButton({
        label: 'Small Size Button',
        size: ButtonSize.SMALL,
      })

      const button = screen.getByRole('button', { name: 'Small Size Button' })
      expect(button).toHaveClass('btn-small')
    })
  })

  describe('States', () => {
    it('should render disabled button', () => {
      renderButton({
        label: 'Disabled Button',
        disabled: true,
      })

      const button = screen.getByRole('button', { name: 'Disabled Button' })
      expect(button).toBeDisabled()
      expect(button).toHaveClass('btn-disabled')
    })

    it('should render hovered button', () => {
      renderButton({
        label: 'Hovered Button',
        hovered: true,
      })

      const button = screen.getByRole('button', { name: 'Hovered Button' })
      expect(button).toHaveClass('btn-hovered')
    })

    it('should render loading button', () => {
      renderButton({
        label: 'Loading Button',
        isLoading: true,
      })

      const button = screen.getByRole('button', { name: /Loading Button/ })
      expect(button).toBeDisabled()
      expect(button).toHaveClass('btn-loading')
      expect(screen.getByTestId('spinner')).toBeInTheDocument()
    })

    it('should render loading button with spinner and label', () => {
      renderButton({
        label: 'Loading Button',
        isLoading: true,
        iconPosition: IconPositionEnum.LEFT,
      })

      const button = screen.getByRole('button', { name: /Loading Button/ })
      expect(button).toBeDisabled()
      expect(screen.getByTestId('spinner')).toBeInTheDocument()
      expect(screen.getByText('Loading Button')).toBeInTheDocument()
    })

    it('should render loading button with spinner only when icon only', () => {
      renderButton({
        isLoading: true,
        icon: fullNextIcon,
      })

      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(screen.getByTestId('spinner')).toBeInTheDocument()
    })

    it('should render transparent button', () => {
      renderButton({
        label: 'Transparent Button',
        transparent: true,
      })

      const button = screen.getByRole('button', { name: 'Transparent Button' })
      expect(button).toHaveClass('btn-transparent')
    })

    it('should render full width button', () => {
      renderButton({
        label: 'Full Width Button',
        fullWidth: true,
      })

      const button = screen.getByRole('button', { name: 'Full Width Button' })
      expect(button).toHaveClass('btn-full-width')
    })

    it('should be disabled when loading', () => {
      renderButton({
        label: 'Loading Button',
        isLoading: true,
        disabled: false,
      })

      const button = screen.getByRole('button', { name: /Loading Button/ })
      expect(button).toBeDisabled()
    })
  })

  describe('Icons', () => {
    it('should render button with icon on the left', () => {
      const { container } = renderButton({
        label: 'Icon Left',
        icon: fullNextIcon,
        iconPosition: IconPositionEnum.LEFT,
      })

      expect(screen.getByText('Icon Left')).toBeInTheDocument()
      const icon = container.querySelector('svg.btn-icon')
      expect(icon).toBeInTheDocument()
    })

    it('should render button with icon on the right', () => {
      const { container } = renderButton({
        label: 'Icon Right',
        icon: fullNextIcon,
        iconPosition: IconPositionEnum.RIGHT,
      })

      expect(screen.getByText('Icon Right')).toBeInTheDocument()
      const icon = container.querySelector('svg.btn-icon')
      expect(icon).toBeInTheDocument()
    })

    it('should render button with icon only (no label)', () => {
      renderButton({
        icon: fullNextIcon,
        iconAlt: 'Next icon',
      })

      const button = screen.getByRole('button')
      expect(button).toHaveClass('btn-icon-only')
      const icon = screen.getByRole('img', { name: 'Next icon' })
      expect(icon).toBeInTheDocument()
    })

    it('should render button with icon and custom icon className', () => {
      const { container } = renderButton({
        label: 'Icon with class',
        icon: fullNextIcon,
        iconClassName: 'custom-icon-class',
      })

      const icon = container.querySelector('svg.btn-icon.custom-icon-class')
      expect(icon).toBeInTheDocument()
    })

    it('should render button with icon alt text', () => {
      renderButton({
        label: 'Icon with alt',
        icon: fullNextIcon,
        iconAlt: 'Custom alt text',
      })

      const icon = screen.getByRole('img', { name: 'Custom alt text' })
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Content rendering', () => {
    it('should render only label when no icon', () => {
      renderButton({
        label: 'Label Only',
      })

      expect(screen.getByText('Label Only')).toBeInTheDocument()
      expect(
        screen.queryByRole('img', { hidden: true })
      ).not.toBeInTheDocument()
    })

    it('should render only icon when no label', () => {
      const { container } = renderButton({
        icon: fullNextIcon,
      })

      const icon = container.querySelector('svg.btn-icon')
      expect(icon).toBeInTheDocument()
      expect(screen.queryByText(/./)).not.toBeInTheDocument()
    })

    it('should render label and icon when both are provided', () => {
      const { container } = renderButton({
        label: 'Label and Icon',
        icon: fullNextIcon,
        iconPosition: IconPositionEnum.LEFT,
      })

      expect(screen.getByText('Label and Icon')).toBeInTheDocument()
      const icon = container.querySelector('svg.btn-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Link rendering', () => {
    it('should render as Link component when to is provided', () => {
      renderButton({
        as: 'a',
        label: 'Link Button',
        to: '/test-path',
      })

      const link = screen.getByRole('link', { name: 'Link Button' })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', '/test-path')
    })

    it('should render as external link when to and isExternal are provided', () => {
      renderButton({
        as: 'a',
        label: 'External Link',
        to: 'https://example.com',
        isExternal: true,
      })

      const link = screen.getByRole('link', { name: 'External Link' })
      expect(link).toBeInTheDocument()
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', 'https://example.com')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should render as section link when to and isSectionLink are provided', () => {
      renderButton({
        as: 'a',
        label: 'Section Link',
        to: '#section',
        isSectionLink: true,
      })

      const link = screen.getByRole('link', { name: 'Section Link' })
      expect(link).toBeInTheDocument()
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', '#section')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should open in new tab when opensInNewTab is true', () => {
      renderButton({
        as: 'a',
        label: 'New Tab Link',
        to: 'https://example.com',
        isExternal: true,
        opensInNewTab: true,
      })

      const link = screen.getByRole('link', { name: 'New Tab Link' })
      expect(link).toHaveAttribute('target', '_blank')
    })

    it('should not have target attribute when opensInNewTab is false', () => {
      renderButton({
        as: 'a',
        label: 'Same Tab Link',
        to: 'https://example.com',
        isExternal: true,
        opensInNewTab: false,
      })

      const link = screen.getByRole('link', { name: 'Same Tab Link' })
      expect(link).not.toHaveAttribute('target')
    })

    it('should handle onClick on link', async () => {
      const handleClick = vi.fn()
      renderButton({
        as: 'a',
        label: 'Clickable Link',
        to: '/test',
        onClick: handleClick,
      })

      const link = screen.getByRole('link', { name: 'Clickable Link' })
      await userEvent.click(link)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should handle onBlur on link', () => {
      const handleBlur = vi.fn()
      renderButton({
        as: 'a',
        label: 'Blur Link',
        to: '/test',
        onBlur: handleBlur,
      })

      const link = screen.getByRole('link', { name: 'Blur Link' })
      link.focus()
      link.blur()
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })

    it('should pass aria-label to link', () => {
      renderButton({
        as: 'a',
        label: 'Aria Link',
        to: '/test',
        'aria-label': 'Custom aria label',
      })

      const link = screen.getByRole('link', { name: 'Custom aria label' })
      expect(link).toHaveAttribute('aria-label', 'Custom aria label')
    })
  })

  describe('Button interactions', () => {
    it('should handle onClick on button', async () => {
      const handleClick = vi.fn()
      renderButton({
        label: 'Clickable Button',
        onClick: handleClick,
      })

      const button = screen.getByRole('button', { name: 'Clickable Button' })
      await userEvent.click(button)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should not call onClick when disabled', async () => {
      const handleClick = vi.fn()
      renderButton({
        label: 'Disabled Button',
        disabled: true,
        onClick: handleClick,
      })

      const button = screen.getByRole('button', { name: 'Disabled Button' })
      await userEvent.click(button)
      expect(handleClick).not.toHaveBeenCalled()
    })

    it('should not call onClick when loading', async () => {
      const handleClick = vi.fn()
      renderButton({
        label: 'Loading Button',
        isLoading: true,
        onClick: handleClick,
      })

      const button = screen.getByRole('button', { name: /Loading Button/ })
      await userEvent.click(button)
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Combined props', () => {
    it('should render button with all props combined', () => {
      renderButton({
        label: 'Complex Button',
        variant: ButtonVariant.SECONDARY,
        color: ButtonColor.NEUTRAL,
        size: ButtonSize.SMALL,
        disabled: false,
        hovered: true,
        transparent: true,
        fullWidth: true,
        icon: fullNextIcon,
        iconPosition: IconPositionEnum.RIGHT,
        iconAlt: 'Next',
        iconClassName: 'custom-class',
      })

      const button = screen.getByRole('button', { name: /Complex Button/ })
      expect(button).toHaveClass('btn-neutral')
      expect(button).toHaveClass('btn-secondary')
      expect(button).toHaveClass('btn-small')
      expect(button).toHaveClass('btn-hovered')
      expect(button).toHaveClass('btn-transparent')
      expect(button).toHaveClass('btn-full-width')
      expect(screen.getByText('Complex Button')).toBeInTheDocument()
      const icon = screen.getByRole('img', { name: 'Next' })
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveClass('custom-class')
    })
  })

  describe('Tooltip', () => {
    it('should render button with tooltip', () => {
      renderButton({
        tooltip: 'Tooltip content',
        icon: fullNextIcon,
        iconAlt: 'Next',
      })

      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('btn-icon-only')
      expect(screen.getByRole('img', { name: 'Next' })).toBeInTheDocument()
      expect(screen.getByText('Tooltip content')).toBeInTheDocument()
    })

    it('should hide tooltip initially and show on focus', async () => {
      renderButton({
        tooltip: 'Tooltip content',
        icon: fullNextIcon,
      })

      expect(screen.getByText('Tooltip content').parentElement).toHaveClass(
        'visually-hidden'
      )

      await userEvent.click(screen.getByRole('button'))

      expect(screen.getByText('Tooltip content').parentElement).not.toHaveClass(
        'visually-hidden'
      )
    })
  })
})
