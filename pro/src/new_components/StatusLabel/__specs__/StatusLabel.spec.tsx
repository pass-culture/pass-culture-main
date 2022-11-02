import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'

import StatusLabel from '../StatusLabel'

const renderStatusLabel = (status: OfferStatus) => {
  return render(<StatusLabel status={status} />)
}

describe('StatusLabel', () => {
  it('should display "expirée" if offer is expired', () => {
    renderStatusLabel(OfferStatus.EXPIRED)
    expect(screen.getByText('expirée')).toBeInTheDocument()
  })
  it('should display "publiée" if offer is active', () => {
    renderStatusLabel(OfferStatus.ACTIVE)
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })
  it('should display draft status label if offer is active', () => {
    renderStatusLabel(OfferStatus.DRAFT)
    expect(screen.getByText('brouillon')).toBeInTheDocument()
  })
  it('should display "désactivée" if offer is inactive', () => {
    renderStatusLabel(OfferStatus.INACTIVE)
    expect(screen.getByText('désactivée')).toBeInTheDocument()
  })
  it('should display "en attente" if offer is pending', () => {
    renderStatusLabel(OfferStatus.PENDING)
    expect(screen.getByText('en attente')).toBeInTheDocument()
  })
  it('should display "refusée" if offer is rejected', () => {
    renderStatusLabel(OfferStatus.REJECTED)
    expect(screen.getByText('refusée')).toBeInTheDocument()
  })
  it('should display "épuisée" if offer is sold out', () => {
    renderStatusLabel(OfferStatus.SOLD_OUT)
    expect(screen.getByText('épuisée')).toBeInTheDocument()
  })
})
