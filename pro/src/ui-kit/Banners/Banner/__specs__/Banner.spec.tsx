import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Banner, { BannerProps } from '../Banner'

describe('Banner', () => {
  const props: BannerProps = {
    closable: true,
    links: [
      {
        href: '/some/site',
        label: 'link label',
        isExternal: true,
        icon: null,
      },
    ],
  }

  it('should render the Banner', () => {
    renderWithProviders(<Banner {...props}>This is the banner content</Banner>)

    // then
    expect(screen.getByText('This is the banner content')).toBeInTheDocument()
    const link = screen.getByRole('link', {
      name: props.links?.[0]?.label,
    })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', props.links?.[0]?.href)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')

    expect(screen.getByRole('img')).toHaveAttribute(
      'aria-label',
      'Masquer le bandeau'
    )
  })

  it('should display close icon with light type', () => {
    props.type = 'light'
    renderWithProviders(
      <Banner {...props}>This is the banner light content</Banner>
    )
    expect(screen.getByRole('img')).toHaveAttribute(
      'aria-label',
      'Masquer le bandeau'
    )
    expect(screen.getByRole('img')).toHaveAttribute('class', 'close-icon')
  })
})
