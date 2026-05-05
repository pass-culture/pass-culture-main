import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { RegistrationStepper } from './RegistrationStepper'

const renderRegistrationStepper = (pathname: string) => {
  return renderWithProviders(<RegistrationStepper />, {
    initialRouterEntries: [pathname],
  })
}

describe('<RegistrationStepper />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderRegistrationStepper(
      '/inscription/compte/creation'
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render 4 steps with correct labels', () => {
    renderRegistrationStepper('/inscription/compte/creation')

    expect(screen.getByText('Votre compte')).toBeInTheDocument()
    expect(screen.getByText('Votre structure')).toBeInTheDocument()
    expect(screen.getByText('Votre activité')).toBeInTheDocument()
    expect(screen.getByText('Validation')).toBeInTheDocument()
  })

  it('should return null when active step is not in the list', () => {
    const { container } = renderRegistrationStepper('/inscription/unknown')

    expect(container).toBeEmptyDOMElement()
  })
})
