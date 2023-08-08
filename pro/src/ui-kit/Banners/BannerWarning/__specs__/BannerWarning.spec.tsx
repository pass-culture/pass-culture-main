import { render, screen } from '@testing-library/react'
import React from 'react'

import BannerWarning, { BannerWarningProps } from '../BannerWarning'

describe('BannerWarning', () => {
  const props: BannerWarningProps = {
    title: 'This is a banner warning',
    links: [{ href: '/some/site', linkTitle: 'linkTitle' }],
  }

  it('should render BannerWarning', () => {
    render(<BannerWarning {...props}>This is the content</BannerWarning>)

    expect(screen.getByText('This is a banner warning')).toBeInTheDocument()
    expect(screen.getByText('This is the content')).toBeInTheDocument()
    const link = screen.getByRole('link', {
      name: props.links?.[0]?.linkTitle,
    })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', props.links?.[0]?.href)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })
})
