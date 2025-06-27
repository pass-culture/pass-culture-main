import { render, screen } from '@testing-library/react'

import { EmailInputRow } from '../EmailInputRow'

describe('EmailInputRow', () => {
  it('should render trash icon by default', () => {
    render(
      <EmailInputRow
        disableForm={false}
        email="test@test.co"
        onChange={() => {}}
      />
    )
    const removeInputIcon = screen.getByRole('button', {
      name: 'Supprimer l’email',
    })
    expect(removeInputIcon).toBeInTheDocument()
  })
})
