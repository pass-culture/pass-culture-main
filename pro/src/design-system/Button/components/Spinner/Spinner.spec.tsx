import { render, screen } from '@testing-library/react'

import { ButtonSize } from '../../types'
import { Spinner, type SpinnerProps } from './Spinner'

const renderSpinner = (props: SpinnerProps = {}) => {
  return render(<Spinner {...props} />)
}

describe('Spinner', () => {
  it('should render the spinner icon', () => {
    renderSpinner()

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('should render the spinner SVG with empty alt and aria-hidden', () => {
    renderSpinner()

    const icon = screen.getByTestId('spinner-svg')
    expect(icon).toBeInTheDocument()
  })

  describe('Size prop', () => {
    it('should render with default size when no size is provided', () => {
      renderSpinner()

      const icon = screen.getByTestId('spinner-svg')
      expect(icon).toHaveAttribute('width', '16')
    })

    it('should render with DEFAULT size', () => {
      renderSpinner({ size: ButtonSize.DEFAULT })

      const icon = screen.getByTestId('spinner-svg')
      expect(icon).toHaveAttribute('width', '16')
    })

    it('should render with SMALL size', () => {
      renderSpinner({ size: ButtonSize.SMALL })

      const icon = screen.getByTestId('spinner-svg')
      expect(icon).toHaveAttribute('width', '14')
    })
  })
})
