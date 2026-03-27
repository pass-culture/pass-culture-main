import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EcoDesignDeclaration } from '../Declaration'

const validatedCriteriaText =
  /Numérotation des fiches pratiques des critères validés/
const nonValidatedCriteriaText =
  /Numérotation des fiches pratiques des critères non validés/
const validatedButtonName = /Critères validés/i
const nonValidatedButtonName = /Critères non validés/i

describe('EcoDesign declaration page', () => {
  it('should display declaration information title', () => {
    renderWithProviders(<EcoDesignDeclaration />)
    expect(
      screen.getByRole('heading', { name: 'Déclaration RGESN' })
    ).toBeInTheDocument()
  })

  it('should toggle validated criteria accordion when button is clicked', async () => {
    renderWithProviders(<EcoDesignDeclaration />)

    const validatedButton = screen.getByRole('button', {
      name: validatedButtonName,
    })

    expect(screen.queryByText(validatedCriteriaText)).not.toBeInTheDocument()

    await userEvent.click(validatedButton)

    expect(screen.getByText(validatedCriteriaText)).toBeVisible()

    await userEvent.click(validatedButton)

    expect(screen.queryByText(validatedCriteriaText)).not.toBeInTheDocument()
  })

  it('should toggle non-validated criteria accordion when button is clicked', async () => {
    renderWithProviders(<EcoDesignDeclaration />)

    const nonValidatedButton = screen.getByRole('button', {
      name: nonValidatedButtonName,
    })

    expect(screen.queryByText(nonValidatedCriteriaText)).not.toBeInTheDocument()

    await userEvent.click(nonValidatedButton)

    expect(screen.getByText(nonValidatedCriteriaText)).toBeVisible()

    await userEvent.click(nonValidatedButton)

    expect(screen.queryByText(nonValidatedCriteriaText)).not.toBeInTheDocument()
  })

  it('should allow both accordions to be open independently', async () => {
    renderWithProviders(<EcoDesignDeclaration />)

    const validatedButton = screen.getByRole('button', {
      name: validatedButtonName,
    })
    const nonValidatedButton = screen.getByRole('button', {
      name: nonValidatedButtonName,
    })

    await userEvent.click(validatedButton)
    await userEvent.click(nonValidatedButton)

    expect(screen.getByText(validatedCriteriaText)).toBeVisible()
    expect(screen.getByText(nonValidatedCriteriaText)).toBeVisible()

    await userEvent.click(validatedButton)

    expect(screen.queryByText(validatedCriteriaText)).not.toBeInTheDocument()
    expect(screen.getByText(nonValidatedCriteriaText)).toBeVisible()
  })
})
