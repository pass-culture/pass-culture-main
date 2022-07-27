import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import Banner, { IBannerProps } from '../Banner'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    const props: IBannerProps = {
      href: '/some/site',
      linkTitle: 'linkTitle',
    }

    it('should render the Banner with the default props', () => {
      // given
      const message = 'message'

      // when
      render(<Banner {...props}>{message}</Banner>)

      // then
      expect(screen.getByText(message)).toBeInTheDocument()
      expect(screen.getByRole('img')).toBeInTheDocument()
      const link = screen.getByRole('link', { name: props.linkTitle })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', props.href)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should change the banner type - attention', () => {
      // given
      const message = 'message'

      // when
      render(<Banner {...props}>{message}</Banner>)

      // then
      expect(screen.getByText(message).closest('div')).toHaveClass(
        'bi-banner attention'
      )
    })

    it('should change the banner type - notification-info', () => {
      // given
      const message = 'message'
      props.type = 'notification-info'

      // when
      render(<Banner {...props}>{message}</Banner>)

      // then
      expect(screen.getByText(message).closest('div')).toHaveClass(
        'bi-banner notification-info'
      )
    })
  })
})
