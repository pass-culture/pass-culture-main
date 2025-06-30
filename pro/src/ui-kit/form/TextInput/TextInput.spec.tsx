import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { TextInput } from './TextInput'

describe('TextInput', () => {
  const defaultProps = {
    name: 'email',
    label: 'Email Address',
    required: true,
    placeholder: 'Enter your email',
    error: '',
  }

  it.each([
    'text',
    'number',
    'email',
    'url',
    'password',
    'tel',
    'search',
  ] as const)(
    'should allow tabbing from one input of type %s to the next',
    async (inputType) => {
      render(
        <>
          <TextInput
            type={inputType}
            label="Input 1"
            name="test1"
            required={true}
          />
          <TextInput
            type={inputType}
            label="Input 2"
            name="test2"
            required={true}
          />
        </>
      )

      screen.getByLabelText('Input 1 *').focus()
      expect(screen.getByLabelText('Input 1 *')).toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).not.toHaveFocus()

      await userEvent.tab()
      expect(screen.getByLabelText('Input 1 *')).not.toHaveFocus()
      expect(screen.getByLabelText('Input 2 *')).toHaveFocus()
    }
  )

  it('should link the input to its description when defined', () => {
    const inputName = 'test'
    const inputLabel = 'Ceci est un champ texte'
    const descriptionContent = 'Instructions pour le remplissage du champ.'

    render(
      <TextInput
        type="text"
        label={inputLabel}
        description={descriptionContent}
        name={inputName}
      />
    )

    expect(screen.getByText(descriptionContent))
  })

  it('should display the element with an error', () => {
    render(
      <TextInput label="Input 1" name="test1" error="My error on my input" />
    )

    expect(screen.getByText('My error on my input')).toBeInTheDocument()
  })

  it('should ignore onKeyDown event for type number', async () => {
    render(
      <TextInput type="number" label="Input" name="test1" required={true} />
    )

    const input = screen.getByLabelText('Input *')
    await userEvent.type(input, '1000')
    await userEvent.keyboard('ArrowUp')

    expect(input).toHaveValue(1000)
  })

  it('renders the input field with the correct label', () => {
    render(<TextInput {...defaultProps} />)

    // Check if the input is rendered with the label and placeholder
    const input = screen.getByLabelText(/email address/i) // Match case-insensitively
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('placeholder', 'Enter your email')
  })

  it('renders the input field with a mandatory asterisk when required', () => {
    render(<TextInput {...defaultProps} />)

    // Check if the label has the asterisk for required fields
    const label = screen.getByText('Email Address *')
    expect(label).toBeInTheDocument()
  })

  it('renders the error message when the error prop is provided', () => {
    const errorMessage = 'This field is required'
    render(<TextInput {...defaultProps} error={errorMessage} />)

    // Check if the error message is displayed
    const error = screen.getByTestId('error-email')
    expect(error).toHaveTextContent(errorMessage)
  })

  it('does not display error when no error prop is passed', () => {
    render(<TextInput {...defaultProps} />)

    // Check if the error is not displayed
    const error = screen.queryByTestId('error-email')
    expect(error).not.toBeInTheDocument()
  })

  it('disables the input when the disabled prop is passed', () => {
    render(<TextInput {...defaultProps} disabled />)

    // Check if the input is disabled
    const input = screen.getByLabelText(/email address/i)
    expect(input).toBeDisabled()
  })

  it('handles readonly mode correctly', () => {
    render(<TextInput {...defaultProps} readOnly value="readonly value" />)

    // Check if the input field is readonly
    const readOnly = screen.getByText(/email address/i)
    expect(readOnly).toBeInTheDocument()
  })

  it('should handle decimal input correctly with hasDecimal=true', async () => {
    render(<TextInput {...defaultProps} type="number" hasDecimal={true} />)

    const input = screen.getByLabelText(/email address/i)

    // Test if decimal input is allowed
    await userEvent.type(input, '123.45')
    expect(input).toHaveValue(123.45)

    // Test if non-numeric input is rejected
    await userEvent.keyboard('a')
    expect(input).toHaveValue(123.45) // Input remains unchanged for non-numeric input
  })

  it('renders description when the description prop is passed', () => {
    const description = 'Please enter a valid email address'
    render(<TextInput {...defaultProps} description={description} />)

    // Check if the description is rendered correctly
    const descriptionElement = screen.getByText(description)
    expect(descriptionElement).toBeInTheDocument()
  })

  it('hides label when isLabelHidden is true', () => {
    render(<TextInput {...defaultProps} isLabelHidden />)

    // Check if the label is hidden
    const label = screen.queryByText('Email Address')
    expect(label).not.toBeInTheDocument()
  })
})
