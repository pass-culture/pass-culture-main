import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { TextInput, type TextInputProps } from '../TextInput/TextInput'

const defaultProps: TextInputProps = {
  label: 'Input label',
  name: 'input',
}

function renderTextInput(props?: Partial<TextInputProps>) {
  return render(<TextInput {...defaultProps} {...props} />)
}

describe('TextInput', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderTextInput()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should show a label, a description and an error message', () => {
    renderTextInput({
      description: 'Input description',
      error: 'Error message',
    })

    expect(screen.getByLabelText('Input label')).toBeInTheDocument()
    expect(screen.getByText('Input description')).toBeInTheDocument()
    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('should show an asterisk if the field is required', () => {
    renderTextInput({
      required: true,
    })

    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('should not show an asterisk if the field is required but the asterisk is disabled', () => {
    renderTextInput({
      required: true,
      requiredIndicator: 'hidden',
    })

    expect(screen.queryByText('*')).not.toBeInTheDocument()
  })

  it('should show the characters count', async () => {
    renderTextInput({
      maxCharactersCount: 100,
    })

    expect(screen.getByText('0/100')).toBeInTheDocument()

    await userEvent.type(screen.getByLabelText('Input label'), 'test')

    expect(screen.getByText('4/100')).toBeInTheDocument()
  })

  it('should show an icon button', () => {
    renderTextInput({
      iconButton: {
        icon: 'fake/icon',
        label: 'Icon button label',
        onClick: () => {},
      },
    })

    expect(
      screen.getByRole('button', { name: 'Icon button label' })
    ).toBeInTheDocument()
  })

  it('should disable the input and its button if the field is disabled', () => {
    renderTextInput({
      disabled: true,
      iconButton: {
        icon: 'fake/icon',
        label: 'Icon button label',
        onClick: () => {},
        disabled: true,
      },
    })

    expect(
      screen.getByRole('button', { name: 'Icon button label' })
    ).toBeDisabled()

    expect(screen.getByLabelText('Input label')).toBeDisabled()
  })
})
