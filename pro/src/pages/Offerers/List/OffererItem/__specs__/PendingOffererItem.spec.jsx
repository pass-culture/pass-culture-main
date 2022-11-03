import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import PendingOffererItem from '../PendingOffererItem'

describe('src | components | pages | Offerers | OffererItem | PendingOffererItem', () => {
  it('should display sentences', () => {
    // when
    render(<PendingOffererItem offerer={{}} />)

    // then
    expect(
      screen.getByText('Rattachement en cours de validation')
    ).toBeInTheDocument()
    expect(screen.getByText('(SIREN: )')).toBeInTheDocument()
  })
})
