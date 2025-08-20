import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { BoxFormLayout } from '../BoxFormLayout'

describe('components:BoxFormLayout', () => {
  it('renders component successfully without accessibility violations', async () => {
    const { container } = render(<BoxFormLayout>I’m a test</BoxFormLayout>)
    expect(screen.getByText('I’m a test')).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })
  it('renders component successfully with required message', () => {
    render(
      <BoxFormLayout>
        I’m a test
        <BoxFormLayout.RequiredMessage />
      </BoxFormLayout>
    )
    expect(screen.getByText('I’m a test')).toBeInTheDocument()
    expect(
      screen.getByText('Tous les champs sont obligatoires.')
    ).toBeInTheDocument()
  })
})
