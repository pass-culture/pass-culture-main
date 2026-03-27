import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EcoDesignPolicy } from '../Policy'

describe('Statement of EcoDesign Policy page', () => {
  it('should display Policy information message', () => {
    renderWithProviders(<EcoDesignPolicy />)
    expect(
      screen.getByRole('heading', {
        name: "Politique d'écoconception au pass Culture",
      })
    ).toBeVisible()
  })
})
