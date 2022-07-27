import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import InternalBanner from '../InternalBanner'

describe('src | components | layout | InternalBanner', () => {
  describe('render', () => {
    let props = {
      subtitle: 'subtitle',
      href: '/some/site',
      linkTitle: 'linkTitle',
    }

    it('should render the InternalBanner with the default props', () => {
      // when
      render(<InternalBanner {...props} />)

      // then
      expect(screen.getByText(props.subtitle)).toBeInTheDocument()
      const link = screen.getByRole('link', { name: props.linkTitle })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', props.href)
      expect(link).not.toHaveAttribute('target', '_blank')
    })

    it('should change the banner type - attention', () => {
      // when
      render(<InternalBanner {...props} />)

      // then
      expect(screen.getByText(props.subtitle).closest('div')).toHaveClass(
        'bi-banner attention'
      )
    })

    it('should change the banner type - notification-info', () => {
      props.type = 'notification-info'

      // when
      render(<InternalBanner {...props} />)

      // then
      expect(screen.getByText(props.subtitle).closest('div')).toHaveClass(
        'bi-banner notification-info'
      )
    })
  })
})
