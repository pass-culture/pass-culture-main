import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Layout } from '../Layout'

const renderLayout = (isImpersonated = false) => {
  renderWithProviders(<Layout />, {
    user: sharedCurrentUserFactory({
      isImpersonated,
    }),
  })
}

describe('App', () => {
  it('should render connect as banner if user has isImpersonated value is true', () => {
    renderLayout(true)

    expect(
      screen.getByText('Vous êtes connecté en tant que :')
    ).toBeInTheDocument()
  })
})
