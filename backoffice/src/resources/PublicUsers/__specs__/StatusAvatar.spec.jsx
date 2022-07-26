import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { StatusAvatar } from '../Components/StatusAvatar'

const renderStatusAvatar = props => render(<StatusAvatar {...props} />)

describe('status avatar', () => {
  it('should display success avatar when status is OK', () => {
    // Given
    const props = { item: { type: 'honor-statement', status: 'ok' } }

    // When
    renderStatusAvatar(props)

    // Then
    expect(screen.getByTestId('CheckCircleOutlineIcon')).toBeInTheDocument()
  })
  it('should display error avatar when status is KO', () => {
    // Given
    const props = { item: { type: 'honor-statement', status: 'ko' } }

    // When
    renderStatusAvatar(props)

    // Then
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument()
  })

  it('should display warning avatar when status is other than ok or ko', () => {
    // Given
    const suspiciousStatus = 'suspicious'
    const props = {
      item: { type: 'honor-statement', status: suspiciousStatus },
    }

    // When
    renderStatusAvatar(props)

    // Then
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument()
    expect(
      screen.getByLabelText(suspiciousStatus.toUpperCase())
    ).toBeInTheDocument()
  })

  it('should display warning avatar when status is undefined', () => {
    // Given
    const props = { item: undefined }

    // When
    renderStatusAvatar(props)

    // Then
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument()
    expect(screen.getByLabelText('Statut inconnu')).toBeInTheDocument()
  })
})
