// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import { RedirectLogin } from '../'

describe('routes:RedirectLogin', () => {
  it('renders component successfully', () => {
    render(<RedirectLogin />)
    const element = screen.getByTestId(/test-redirect-login/i)
    expect(element).toBeInTheDocument()
  })
})
