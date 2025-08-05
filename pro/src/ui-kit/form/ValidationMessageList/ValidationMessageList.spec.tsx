import { screen } from '@testing-library/react'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import {
  getPasswordRuleLabel,
  PasswordValidationCheck,
} from 'ui-kit/form/PasswordInput/validation'
import { axe } from 'vitest-axe'

import {
  ValidationMessageList,
  ValidationMessageListProps,
} from './ValidationMessageList'

const defaultProps: ValidationMessageListProps = {
  passwordValue: 'a', // ggignore
  hasError: false,
}

const renderValidationMessageList = (
  props?: Partial<ValidationMessageListProps>,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(
    <ValidationMessageList {...defaultProps} {...props} />,
    {
      ...options,
    }
  )
}

describe('<ValidationMessageList />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderValidationMessageList()

    expect(await axe(container)).toHaveNoViolations()
  })

  describe('validation cases', () => {
    // Generates tests names for each test case
    const generateTestName = ({
      passwordValue,
      passwordRuleLabel,
      shouldDisplayAnError,
    }: {
      passwordValue: string
      passwordRuleLabel: string
      shouldDisplayAnError: boolean
    }) => {
      return `password "${passwordValue}" should ${shouldDisplayAnError ? '' : 'not '} display an error for the rule "${passwordRuleLabel}"`
    }

    const testCases = [
      // At least 1 lower case character
      {
        passwordValue: 'a', // ggignore
        passwordRuleLabel: PasswordValidationCheck.LOWER_CASE,
        shouldDisplayAnError: false,
      },
      {
        passwordValue: 'A', // ggignore
        passwordRuleLabel: PasswordValidationCheck.LOWER_CASE,
        shouldDisplayAnError: true,
      },
      // At least 1 upper case character
      {
        passwordValue: 'A', // ggignore
        passwordRuleLabel: PasswordValidationCheck.UPPER_CASE,
        shouldDisplayAnError: false,
      },
      {
        passwordValue: 'a', // ggignore
        passwordRuleLabel: PasswordValidationCheck.UPPER_CASE,
        shouldDisplayAnError: true,
      },
      // At least a minimum of 12 characters (defined inside the validation rule)
      {
        passwordValue: '12345', // ggignore
        passwordRuleLabel: PasswordValidationCheck.LENGTH,
        shouldDisplayAnError: true,
      },
      {
        passwordValue: '123456789101112', // ggignore
        passwordRuleLabel: PasswordValidationCheck.LENGTH,
        shouldDisplayAnError: false,
      },
      // At least 1 number
      {
        passwordValue: 'abc', // ggignore
        passwordRuleLabel: PasswordValidationCheck.NUMBER,
        shouldDisplayAnError: true,
      },
      {
        passwordValue: 'abc1d', // ggignore
        passwordRuleLabel: PasswordValidationCheck.NUMBER,
        shouldDisplayAnError: false,
      },
      // At least 1 special character
      {
        passwordValue: 'azerty456', // ggignore
        passwordRuleLabel: PasswordValidationCheck.SYMBOLE,
        shouldDisplayAnError: true,
      },
      {
        passwordValue: 'azerty!456', // ggignore
        passwordRuleLabel: PasswordValidationCheck.SYMBOLE,
        shouldDisplayAnError: false,
      },
      {
        passwordValue: 'azerty$456', // ggignore
        passwordRuleLabel: PasswordValidationCheck.SYMBOLE,
        shouldDisplayAnError: false,
      },
    ]

    testCases.forEach(
      ({ passwordValue, passwordRuleLabel, shouldDisplayAnError }) => {
        it(
          generateTestName({
            passwordValue,
            passwordRuleLabel,
            shouldDisplayAnError,
          }),
          () => {
            renderValidationMessageList({ passwordValue })

            const successMessage = screen.queryByTestId(
              `success-${getPasswordRuleLabel(passwordRuleLabel)}`
            )
            const errorMessage = screen.queryByTestId(
              `error-${getPasswordRuleLabel(passwordRuleLabel)}`
            )

            if (shouldDisplayAnError) {
              expect(errorMessage).toBeInTheDocument()
              expect(successMessage).not.toBeInTheDocument()
            } else {
              expect(errorMessage).not.toBeInTheDocument()
              expect(successMessage).toBeInTheDocument()
            }
          }
        )
      }
    )
  })
})
