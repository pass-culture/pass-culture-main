import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { ImageEditor } from './ImageEditor'

// Mocking the dependencies
vi.mock('ui-kit/form/Slider/Slider', () => ({
  Slider: vi.fn(() => <input type="range" data-testid="slider" />),
}))

vi.mock('./canvas', () => ({
  CanvasTools: vi.fn().mockImplementation(() => ({
    drawArea: vi.fn(),
  })),
}))

describe('ImageEditor Component', () => {
  const mockImage = new File(['image'], 'image.jpg', { type: 'image/jpeg' })

  const defaultProps = {
    image: mockImage,
    canvasHeight: 500,
    canvasWidth: 500,
    cropBorderColor: 'red',
    cropBorderHeight: 20,
    cropBorderWidth: 20,
    maxScale: 4,
  }

  it('renders correctly', () => {
    render(<ImageEditor {...defaultProps} />)

    expect(screen.getByLabelText("Editeur d'image")).toBeInTheDocument()
    expect(screen.getByTestId('slider')).toBeInTheDocument()
  })

  it('handles window resize and adjusts canvas size', () => {
    render(<ImageEditor {...defaultProps} />)

    expect(screen.getByLabelText("Editeur d'image")).toHaveAttribute(
      'width',
      '540'
    )
    expect(screen.getByLabelText("Editeur d'image")).toHaveAttribute(
      'height',
      '540'
    )
  })

  it('handles zoom slider change correctly', () => {
    render(<ImageEditor {...defaultProps} />)

    const slider = screen.getByTestId('slider')

    fireEvent.change(slider, { target: { value: 2 } })

    expect(slider).toHaveValue('2')
  })
})
