import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { PasswordInput, type PasswordInputProps } from './PasswordInput'

const defaultProps: PasswordInputProps = {
  label: 'Input label',
  name: 'input',
  value: '',
  onChange: () => {},
}

function renderPasswordInput(props?: Partial<PasswordInputProps>) {
  return render(<PasswordInput {...defaultProps} {...props} />)
}

describe('PasswordInput', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderPasswordInput()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should show a label, a description and an error message', () => {
    renderPasswordInput({
      description: 'Input description',
      error: 'Error message',
    })

    expect(screen.getByLabelText('Input label')).toBeInTheDocument()
    expect(screen.getByText('Input description')).toBeInTheDocument()
    expect(screen.getByText('Error message')).toBeInTheDocument()
  })

  it('should show an asterisk if the field is required', () => {
    renderPasswordInput({
      required: true,
    })

    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('should not show an asterisk if the field is required but the asterisk is disabled', () => {
    renderPasswordInput({
      required: true,
      requiredIndicator: 'hidden',
    })

    expect(screen.queryByText('*')).not.toBeInTheDocument()
  })

  it('should disable the input and its button if the field is disabled', () => {
    renderPasswordInput({
      disabled: true,
    })

    expect(screen.getByLabelText('Input label')).toBeDisabled()
  })

  it('should show validation list', () => {
    renderPasswordInput({
      displayValidation: true,
    })

    expect(
      screen.getByText(/Le mot de passe doit comporter :/)
    ).toBeInTheDocument()
  })
})
