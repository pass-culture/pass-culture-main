import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { StatusBadge } from '../Components/StatusBadge'

const renderStatusBadge = props => render(<StatusBadge {...props} />)

describe('status badge', () => {
  it('should display success when active is OK', () => {
    // Given
    const props = { active: true }

    // When
    renderStatusBadge(props)

    // Then
    expect(screen.getByTestId('CheckCircleOutlineIcon')).toBeInTheDocument()
    expect(screen.getByText('Actif')).toBeInTheDocument()
  })

  it('should display error badge by default', () => {
    // Given
    const props = {}

    // When
    renderStatusBadge(props)

    // Then
    expect(screen.getByTestId('HighlightOffIcon')).toBeInTheDocument()
    expect(screen.getByText('Suspendu')).toBeInTheDocument()
  })
})
