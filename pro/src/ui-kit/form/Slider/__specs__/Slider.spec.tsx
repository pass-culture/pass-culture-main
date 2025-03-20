import { render, screen } from '@testing-library/react'

import { Slider, SliderProps } from '../Slider'

const renderSlider = (props: SliderProps) => render(<Slider {...props} />)

describe('Slider', () => {
  const defaultProps = {
    name: 'sliderValue',
    scale: 'km',
    displayValue: false,
  }
  it('should render default min and max value with scale', () => {
    renderSlider(defaultProps)
    expect(screen.getByText('0 km')).toBeInTheDocument()
    expect(screen.getByText('100 km')).toBeInTheDocument()
  })

  it('should render custom min and max value with scale', () => {
    renderSlider({ ...defaultProps, min: 1, max: 5 })
    expect(screen.getByText('1 km')).toBeInTheDocument()
    expect(screen.getByText('5 km')).toBeInTheDocument()
  })

  it('should display the value', () => {
    renderSlider({
      ...defaultProps,
      min: 1,
      max: 5,
      displayValue: true,
    })

    expect(screen.getByText(/1 km/)).toBeInTheDocument()
  })
})
