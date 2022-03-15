---
to: <%= absPath %>/__specs__/<%= component_name %>.spec.tsx
---
// react-testing-library doc: https://testing-library.com/docs/react-testing-library/api
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import { <%= component_name %> } from '../'

describe('<%= category %>:<%= component_name %>', () => {
  it('renders component successfully', () => {
    render(<<%= component_name %> />)
    const element = screen.getByTestId(/<%= testId %>/i)
    expect(element).toBeInTheDocument()
  })
})
