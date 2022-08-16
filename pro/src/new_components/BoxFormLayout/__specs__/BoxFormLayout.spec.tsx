// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import { BoxFormLayout } from '../'

describe('new_components:BoxFormLayout', () => {
  it('renders component successfully', () => {
    render(<BoxFormLayout>I'm a test</BoxFormLayout>)
    const element = screen.getByText("I'm a test")
    expect(element).toBeInTheDocument()
  })
})
