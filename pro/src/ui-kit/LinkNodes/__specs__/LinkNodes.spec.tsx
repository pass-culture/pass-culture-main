import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import fullMailIcon from '@/icons/full-mail.svg'

import { LinkNode } from '../LinkNodes'

describe('LinkNodes', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <LinkNode href="/some/site" label="link label" isExternal />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display an external link with icon', () => {
    renderWithProviders(
      <LinkNode href="/some/site" label="link label" isExternal />
    )

    const link = screen.getByRole('link', {
      name: /link label/,
    })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/some/site')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(screen.getByRole('img')).toHaveAttribute(
      'aria-label',
      'Nouvelle fenêtre'
    )
  })

  it('should display an internal link with icon', () => {
    renderWithProviders(<LinkNode href="/some/site" label="link label" />)

    const link = screen.getByRole('link', {
      name: /link label/,
    })
    expect(link).toHaveAttribute('href', '/some/site')
  })

  it('should display a custom external link with icon', () => {
    renderWithProviders(
      <LinkNode
        href="mailto:support-pro@passculture.app"
        isExternal
        icon={{ src: fullMailIcon, alt: '' }}
        label="Contacter le support"
      />
    )

    const link = screen.getByRole('link', {
      name: /Contacter le support/,
    })
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(screen.getByRole('img')).toHaveAttribute(
      'aria-label',
      'Nouvelle fenêtre'
    )
  })
})
