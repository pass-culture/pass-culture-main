import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import Banner, { IBannerProps } from '../Banner'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    const props: IBannerProps = {
      links: [{ href: '/some/site', linkTitle: 'linkTitle' }],
    }

    it('should render the Banner with the default props', () => {
      // given
      const message = 'message'

      // when
      render(<Banner {...props}>{message}</Banner>)

      // then
      expect(screen.getByText(message)).toBeInTheDocument()
      const link = screen.getByRole('link', {
        name: props.links?.[0]?.linkTitle,
      })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', props.links?.[0]?.href)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })
})
