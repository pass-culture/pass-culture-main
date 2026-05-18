import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignupStepper } from './SignupStepper'

const renderSignupStepper = (pathname: string) => {
  return renderWithProviders(<SignupStepper />, {
    initialRouterEntries: [pathname],
  })
}

describe('<SignupStepper />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSignupStepper('/prefix/creation')

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render 4 steps with correct labels', () => {
    renderSignupStepper('/prefix/account-creation')

    expect(screen.getByText('Votre compte')).toBeInTheDocument()
    expect(screen.getByText('Votre structure')).toBeInTheDocument()
    expect(screen.getByText('Votre activité')).toBeInTheDocument()
    expect(screen.getByText('Validation')).toBeInTheDocument()
  })

  it('should return null when active step is not in the list', () => {
    const { container } = renderSignupStepper('/prefix/unknown')

    expect(container).toBeEmptyDOMElement()
  })
})
