// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { ResetEmailBanner } from '../'

describe('new_components:ResetEmailBanner', () => {
  it('renders component successfully', async () => {
    render(<ResetEmailBanner email="test@example.com" />)

    expect(screen.getByRole('link')).toBeInTheDocument()
  })
})
