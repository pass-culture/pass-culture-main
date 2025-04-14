import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRef } from 'react'

import { RadioButton } from './RadioButton'

describe('RadioButton', () => {
  it('should display a radio input', () => {
    render(<RadioButton label="Radio 1" name="myField" value="value1" />)

    expect(screen.getByLabelText('Radio 1')).toBeInTheDocument()
  })

  it('should pass the ref correctly to the input element', () => {
    const TestComponent = () => {
      const ref = useRef<HTMLInputElement>(null)
      return (
        <RadioButton ref={ref} label="Radio 1" name="myField" value="value1" />
      )
    }

    render(<TestComponent />)
    const input = screen.getByLabelText('Radio 1')
    expect(input).toBeInTheDocument()
  })

  it('should pass onChange and onBlur events to BaseRadio', async () => {
    const handleChange = vi.fn()
    const handleBlur = vi.fn()

    render(
      <RadioButton
        label="Radio 1"
        name="myField"
        value="value1"
        onChange={handleChange}
        onBlur={handleBlur}
      />
    )

    const input = screen.getByLabelText('Radio 1')

    await userEvent.click(input)
    expect(handleChange).toHaveBeenCalledTimes(1)

    await userEvent.tab()
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })
})
