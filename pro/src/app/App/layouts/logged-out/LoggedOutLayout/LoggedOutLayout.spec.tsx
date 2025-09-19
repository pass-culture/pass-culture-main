import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { LoggedOutLayout } from './LoggedOutLayout'

const renderLoggedOutLayout = () => {
  return renderWithProviders(<LoggedOutLayout mainHeading="Connexion" />)
}

describe('LoggedOutLayout', () => {
  it('should always render a main landmark and a heading level 1', () => {
    renderLoggedOutLayout()

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })
})
