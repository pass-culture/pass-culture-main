import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import LocationViewer from '../LocationViewer'

describe('src | components | pages | Venue | fields | LocationViewer', () => {
  it('should diplay an input', () => {
    // when
    render(<LocationViewer />)

    // then
    const input = screen.getByRole('textbox')

    expect(input).toHaveValue('')
    expect(input).toHaveAttribute('readonly')
  })
})
