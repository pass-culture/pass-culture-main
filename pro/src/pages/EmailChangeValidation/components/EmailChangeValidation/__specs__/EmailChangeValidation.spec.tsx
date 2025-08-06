import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EmailChangeValidationScreen } from '../EmailChangeValidation'

describe('screens:EmailChangeValidation', () => {
  it('renders component successfully when success', () => {
    renderWithProviders(<EmailChangeValidationScreen isSuccess={true} />)

    expect(
      screen.getByText(
        /Merci d’avoir confirmé votre changement d’adresse email./,
        {
          selector: 'p',
        }
      )
    ).toBeInTheDocument()
  })

  it('renders component successfully when not success', () => {
    renderWithProviders(<EmailChangeValidationScreen isSuccess={false} />)
    expect(
      screen.getByText(/Votre adresse email n’a pas été modifiée car le lien/, {
        selector: 'p',
      })
    ).toBeInTheDocument()
  })
})
