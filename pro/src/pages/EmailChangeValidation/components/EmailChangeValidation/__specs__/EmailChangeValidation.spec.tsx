import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { EmailChangeValidationScreen } from '../EmailChangeValidation'

describe('screens:EmailChangeValidation', () => {
  it('renders component successfully when success', () => {
    renderWithProviders(<EmailChangeValidationScreen isSuccess={true} />)

    expect(
      screen.getByText('Et voilà !', {
        selector: 'h1',
      })
    ).toBeInTheDocument()
  })

  it('renders component successfully when not success', () => {
    renderWithProviders(<EmailChangeValidationScreen isSuccess={false} />)
    expect(
      screen.getByText('Votre lien a expiré !', {
        selector: 'h1',
      })
    ).toBeInTheDocument()
  })
})
