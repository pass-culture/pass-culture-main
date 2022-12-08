import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import Tooltip from '../Tooltip'

describe('Tooltip', () => {
  it('should render without error', () => {
    render(
      <Tooltip id="someid" content="Contenu du tooltip">
        Enfant
      </Tooltip>
    )

    expect(screen.getByText('Enfant')).toBeInTheDocument()
  })
})
