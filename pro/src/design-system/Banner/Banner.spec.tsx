import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import fullLinkIcon from '@/icons/full-link.svg'

import turtle from '../assets/turtle.png'
import { Banner, type BannerProps, BannerVariants } from './Banner'

const renderBanner = (props: BannerProps) => {
  return renderWithProviders(<Banner {...props} />)
}

const props: BannerProps = {
  title: 'Titre important très long très long très long très long très',
  description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
  actions: [
    { label: 'En savoir plus', href: '#', icon: fullLinkIcon, type: 'link' },
    { label: 'En savoir moins', href: '#', icon: fullLinkIcon, type: 'link' },
  ],
  imageSrc: turtle,
  variant: BannerVariants.DEFAULT,
  closable: true,
}

describe('Banner', () => {
  it('should have an accessible structure', async () => {
    const { container } = renderBanner(props)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the title, description, links, image and close button', () => {
    renderBanner(props)
    expect(
      screen.getByText(
        'Titre important très long très long très long très long très'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'En savoir plus' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'En savoir moins' })
    ).toBeInTheDocument()
    expect(screen.getByAltText('')).toHaveAttribute(
      'src',
      '/src/design-system/assets/turtle.png'
    )
    expect(
      screen.getByRole('button', { name: 'Fermer la bannière d’information' })
    ).toBeInTheDocument()
  })

  it('should not display the image and close button when not provided', () => {
    renderBanner({
      ...props,
      imageSrc: undefined,
      closable: false,
    })
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Fermer la bannière d’information' })
    ).not.toBeInTheDocument()
  })

  it('should render correctly with different variants', () => {
    Object.values(BannerVariants).forEach((variant, index) => {
      renderBanner({ ...props, title: `Titre ${variant}`, variant })
      expect(screen.getAllByTestId('banner')[index]).toHaveClass(variant)
    })
  })

  it('should target links correctly based on the external prop', () => {
    renderBanner({
      ...props,
      actions: [
        {
          label: 'Internal Link',
          href: '/internal',
          isExternal: false,
          type: 'link',
        },
        {
          label: 'External Link',
          href: 'https://external.com',
          isExternal: true,
          type: 'link',
        },
      ],
    })

    const internalLink = screen.getByRole('link', { name: 'Internal Link' })
    const externalLink = screen.getByRole('link', { name: 'External Link' })

    expect(internalLink).toHaveAttribute('target', '_self')
    expect(internalLink).not.toHaveAttribute('rel')

    expect(externalLink).toHaveAttribute('target', '_blank')
    expect(externalLink).toHaveAttribute('rel', 'noopener noreferrer')
  })
})
