// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api

import { render, screen } from '@testing-library/react'
import React from 'react'

import { BoxFormLayout } from '../'

describe('components:BoxFormLayout', () => {
  it('renders component successfully', () => {
    render(<BoxFormLayout>I’m a test</BoxFormLayout>)
    expect(screen.getByText('I’m a test')).toBeInTheDocument()
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
      screen.getByText('Tous les champs suivis d’un * sont obligatoires.')
    ).toBeInTheDocument()
  })
})
