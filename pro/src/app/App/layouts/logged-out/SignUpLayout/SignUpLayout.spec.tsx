import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SignUpLayout } from './SignUpLayout'

const renderLayout = () => {
  renderWithProviders(<SignUpLayout mainHeading="Connexion" />)
}

describe('SignUpLayout', () => {
  it('should always render a main landmark and a heading level 1', () => {
    renderLayout()

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  it('should render sign up banners', () => {
    renderLayout()

    expect(screen.getByTestId('sign-up-header')).toBeInTheDocument()
    expect(screen.getByTestId('sign-up-logo')).toBeInTheDocument()
  })
})
