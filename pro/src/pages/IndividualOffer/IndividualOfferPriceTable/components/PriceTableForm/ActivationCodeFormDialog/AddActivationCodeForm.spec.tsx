import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AddActivationCodeForm } from './AddActivationCodeForm'

const LABELS = {
  template: 'Télécharger le gabarit (.csv, 50ko)',
}

describe('AddActivationCodeForm', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <AddActivationCodeForm errorMessage="" errorTitle="" />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render helper banner when no error', () => {
    renderWithProviders(<AddActivationCodeForm errorMessage="" errorTitle="" />)

    expect(
      screen.getByRole('link', { name: LABELS.template })
    ).toBeInTheDocument()
  })

  it('should show error block when errorMessage provided', () => {
    renderWithProviders(
      <AddActivationCodeForm
        errorMessage="Wrong format"
        errorTitle="Format invalide"
      />
    )

    expect(screen.getByText('Format invalide')).toBeInTheDocument()
    expect(screen.getByText('Wrong format')).toBeInTheDocument()
  })
})
