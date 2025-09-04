import { screen, within } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { PasswordInput, type PasswordInputProps } from './PasswordInput'

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

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
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

    expect(
      screen.getByText('Choisissez un mot de passe fort et difficile à deviner')
    ).toBeInTheDocument()
  })
})
