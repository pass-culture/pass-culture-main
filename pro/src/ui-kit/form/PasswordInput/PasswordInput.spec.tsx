import { screen, within } from '@testing-library/react'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { axe } from 'vitest-axe'

import { PasswordInput, PasswordInputProps } from './PasswordInput'

const defaultProps: PasswordInputProps = {
  label: 'Mot de passe',
  name: 'password',
}

const renderPasswordInput = (
  props?: Partial<PasswordInputProps>,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<PasswordInput {...defaultProps} {...props} />, {
    ...options,
  })
}

describe('<PasswordInput />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderPasswordInput()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render with an error message', () => {
    renderPasswordInput({ error: 'Une erreur est survenue' })

    const alertElement = screen.getByRole('alert')

    expect(alertElement).toBeInTheDocument()
    expect(
      within(alertElement).getByText('Une erreur est survenue')
    ).toBeInTheDocument()
  })

  it('should render with a description', () => {
    renderPasswordInput({
      description: 'Choisissez un mot de passe fort et difficile à deviner',
    })

    expect(screen.getByTestId('description-password')).toHaveTextContent(
      'Choisissez un mot de passe fort et difficile à deviner'
    )
  })
})
