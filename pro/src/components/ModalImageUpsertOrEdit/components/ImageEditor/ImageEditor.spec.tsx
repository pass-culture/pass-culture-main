import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import { ImageEditor, map } from './ImageEditor'

vi.mock('use-debounce', async () => ({
  ...(await vi.importActual('use-debounce')),
  useDebouncedCallback: vi.fn((fn) => fn),
}))

describe('ImageEditor', () => {
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

  it('calls onChangeDone when the image is changed via slider', () => {
    const onChangeDone = vi.fn()
    render(<ImageEditor {...defaultProps} onChangeDone={onChangeDone} />)

    const slider = screen.getByTestId('slider')
    fireEvent.change(slider, { target: { value: 2 } })

    expect(onChangeDone).toHaveBeenCalled()
  })

  it('displays a warning when scale is disabled', () => {
    render(<ImageEditor {...defaultProps} initialScale={0} maxScale={1} />)

    expect(
      screen.getByText('L’image est trop petite pour utiliser le zoom.')
    ).toBeInTheDocument()
  })
})

describe('ImageEditor:map', () => {
  it('maps values correctly', () => {
    const result = map(5, 0, 10, 0, 100)
    expect(result).toBe(50)
  })

  it('clamps values correctly when above max', () => {
    const result = map(15, 0, 10, 0, 100)
    expect(result).toBe(100)
  })

  it('clamps values correctly when below min', () => {
    const result = map(-5, 0, 10, 0, 100)
    expect(result).toBe(0)
  })
})
