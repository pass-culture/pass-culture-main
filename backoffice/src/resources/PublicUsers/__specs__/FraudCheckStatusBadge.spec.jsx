import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { FraudCheckStatusBadge } from '../Components/FraudCheckStatusBadge'
import { FraudCheckStatus } from '../types'

const renderFraudCheckStatusBadge = props =>
  render(<FraudCheckStatusBadge {...props} />)

describe('fraud check status badge', () => {
  it('should display success chip when status is OK', () => {
    // Given
    const props = { active: true, fraudCheckStatus: FraudCheckStatus.OK }

    // When
    renderFraudCheckStatusBadge(props)

    // Then
    expect(screen.getByTestId('CheckCircleOutlineIcon')).toBeInTheDocument()
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('should display error chip when status is KO', () => {
    // Given
    const props = { active: false, fraudCheckStatus: FraudCheckStatus.KO }

    // When
    renderFraudCheckStatusBadge(props)

    // Then
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument()
    expect(screen.getByText('KO')).toBeInTheDocument()
  })

  it('should display warning chip when status is other than OK or KO', () => {
    // Given
    const props = { status: false, fraudCheckStatus: FraudCheckStatus.STARTED }

    // When
    renderFraudCheckStatusBadge(props)

    // Then
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument()
    expect(screen.getByText('STARTED')).toBeInTheDocument()
  })
})
