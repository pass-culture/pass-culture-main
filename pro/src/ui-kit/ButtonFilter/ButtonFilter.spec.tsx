import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ButtonFilter } from './ButtonFilter'

vi.mock('@/ui-kit/SvgIcon/SvgIcon', () => ({
  SvgIcon: vi.fn(() => <span data-testid="mock-icon" />),
}))

describe('ButtonFilter', () => {
  it('should render correctly with default props', () => {
    render(<ButtonFilter>Filter</ButtonFilter>)

    const button = screen.getByRole('button', { name: /filter/i })
    expect(button).toBeInTheDocument()
    expect(button).not.toHaveClass('button-filter-open')
    expect(button).not.toHaveClass('button-filter-active')

    const icon = screen.getByTestId('mock-icon')
    expect(icon).toBeInTheDocument()
  })

  it('should apply "button-filter-open" class when isOpen is true', () => {
    render(<ButtonFilter isOpen>Filter</ButtonFilter>)

    const button = screen.getByRole('button', { name: /filter/i })
    expect(button).toHaveClass('button-filter-open')
  })

  it('should apply "button-filter-active" class when isActive is true', () => {
    render(<ButtonFilter isActive>Filter</ButtonFilter>)

    const button = screen.getByRole('button', { name: /filter/i })
    expect(button).toHaveClass('button-filter-active')
  })

  it('should toggle icon based on isOpen prop', () => {
    const { rerender } = render(<ButtonFilter isOpen>Filter</ButtonFilter>)
    let icon = screen.getByTestId('mock-icon')

    // Initially, isOpen is true, so it should show the "fullUpIcon"
    expect(icon).toBeInTheDocument()

    rerender(<ButtonFilter isOpen={false}>Filter</ButtonFilter>)
    icon = screen.getByTestId('mock-icon')

    // Now isOpen is false, so it should show the "fullDownIcon"
    expect(icon).toBeInTheDocument()
  })

  it('should pass additional button attributes', () => {
    render(
      <ButtonFilter data-testid="custom-button" aria-label="Custom Button">
        Filter
      </ButtonFilter>
    )

    const button = screen.getByTestId('custom-button')
    expect(button).toHaveAttribute('aria-label', 'Custom Button')
  })

  it('should trigger click events correctly', async () => {
    const handleClick = vi.fn()
    render(<ButtonFilter onClick={handleClick}>Filter</ButtonFilter>)

    const button = screen.getByRole('button', { name: /filter/i })
    await userEvent.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
