import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EcoDesignDeclaration } from '../Declaration'

const validatedCriteriaText =
  /Numérotation des fiches pratiques des critères validés/
const nonValidatedCriteriaText =
  /Numérotation des fiches pratiques des critères non validés/
const validatedButtonName = /Critères validés/i
const nonValidatedButtonName = /Critères non validés/i

describe('EcoDesign declaration page', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<EcoDesignDeclaration />)

    expect(await axe(container)).toHaveNoViolations()
  })

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

  it.each([
    [validatedButtonName, validatedCriteriaText],
    [nonValidatedButtonName, nonValidatedCriteriaText],
  ])(
    'should close the criteria accordion and keep focus on its button when Escape is pressed',
    async (buttonName, criteriaText) => {
      renderWithProviders(<EcoDesignDeclaration />)

      const button = screen.getByRole('button', { name: buttonName })
      await userEvent.click(button)

      expect(button).toHaveAttribute('aria-expanded', 'true')

      await userEvent.keyboard('{Escape}')

      expect(screen.queryByText(criteriaText)).not.toBeInTheDocument()
      expect(button).toHaveAttribute('aria-expanded', 'false')
      expect(button).toHaveFocus()
    }
  )

  it.each([
    [validatedButtonName, validatedCriteriaText],
    [nonValidatedButtonName, nonValidatedCriteriaText],
  ])(
    'should close the criteria accordion when focus moves outside it',
    async (buttonName, criteriaText) => {
      renderWithProviders(<EcoDesignDeclaration />)

      await userEvent.click(screen.getByRole('button', { name: buttonName }))
      await userEvent.click(
        screen.getByRole('heading', { name: 'Déclaration RGESN' })
      )

      expect(screen.queryByText(criteriaText)).not.toBeInTheDocument()
    }
  )

  it('should close each criteria accordion when focus moves to the other button', async () => {
    renderWithProviders(<EcoDesignDeclaration />)

    const validatedButton = screen.getByRole('button', {
      name: validatedButtonName,
    })
    const nonValidatedButton = screen.getByRole('button', {
      name: nonValidatedButtonName,
    })

    await userEvent.click(validatedButton)
    await userEvent.tab()

    expect(nonValidatedButton).toHaveFocus()
    expect(screen.queryByText(validatedCriteriaText)).not.toBeInTheDocument()

    await userEvent.click(nonValidatedButton)
    await userEvent.tab({ shift: true })

    expect(validatedButton).toHaveFocus()
    expect(screen.queryByText(nonValidatedCriteriaText)).not.toBeInTheDocument()
  })
})
