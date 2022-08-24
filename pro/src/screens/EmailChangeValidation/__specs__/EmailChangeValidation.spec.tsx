// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { EmailChangeValidationScreen } from '../'

describe('screens:EmailChangeValidation', () => {
  it('renders component successfully when success', async () => {
    render(
      <MemoryRouter>
        <EmailChangeValidationScreen isSuccess={true} />
      </MemoryRouter>
    )

    expect(
      screen.getByText('Et voilà !', {
        selector: 'h1',
      })
    ).toBeInTheDocument()
  })
  it('renders component successfully when not success', () => {
    render(
      <MemoryRouter>
        <EmailChangeValidationScreen isSuccess={false} />
      </MemoryRouter>
    )
    expect(
      screen.getByText('Votre lien a expiré !', {
        selector: 'h1',
      })
    ).toBeInTheDocument()
  })
})
