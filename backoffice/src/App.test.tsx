import { render, screen } from '@testing-library/react'
import React from 'react'

import { App } from './App'
import { superFlushWithAct } from './tests/utils'

test('renders learn react link', () => {
  render(<App />)

  const linkElement = screen.getByText(/Aller au contenu/i)
  superFlushWithAct()

  expect(linkElement).toBeInTheDocument()
})
