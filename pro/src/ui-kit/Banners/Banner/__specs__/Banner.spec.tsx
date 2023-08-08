import { render, screen } from '@testing-library/react'
import React from 'react'

import fullNextIcon from 'icons/full-next.svg'

import Banner, { BannerProps } from '../Banner'

describe('Banner', () => {
  const props: BannerProps = {
    closable: true,
    links: [{ href: '/some/site', linkTitle: 'linkTitle', icon: fullNextIcon }],
  }

  it('should render the Banner', () => {
    render(<Banner {...props}>This is the banner content</Banner>)

    // then
    expect(screen.getByText('This is the banner content')).toBeInTheDocument()
    const link = screen.getByRole('link', {
      name: props.links?.[0]?.linkTitle,
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
})
