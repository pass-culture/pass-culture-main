import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignUpLayout } from './SignUpLayout'

const renderLayout = () => {
  renderWithProviders(<SignUpLayout mainHeading="Connexion" />)
}

describe('SignUpLayout', () => {
  it('should render sign up banners', () => {
    renderLayout()

    expect(screen.getByTestId('sign-up-header')).toBeInTheDocument()
    expect(screen.getByTestId('sign-up-logo')).toBeInTheDocument()
  })
})
