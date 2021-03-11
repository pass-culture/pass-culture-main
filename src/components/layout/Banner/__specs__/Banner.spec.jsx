import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    let props = {
      message: 'message',
      href: '/some/site',
      linkTitle: 'linkTitle',
    }

    it('should render the Banner with the default props', () => {
      // when
      render(<Banner {...props} />)

      // then
      expect(screen.getByText(props.message)).toBeInTheDocument()
      expect(screen.getByRole('img')).toBeInTheDocument()
      const link = screen.getByRole('link', { name: props.linkTitle })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', props.href)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should change the banner type - attention', () => {
      // when
      render(<Banner {...props} />)

      // then
      expect(screen.getByText(props.message).closest('div')).toHaveAttribute(
        'class',
        'bi-banner attention'
      )
    })

    it('should change the banner type - notification-info', () => {
      props.type = 'notification-info'

      // when
      render(<Banner {...props} />)

      // then
      expect(screen.getByText(props.message).closest('div')).toHaveAttribute(
        'class',
        'bi-banner notification-info'
      )
    })
  })
})
