import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers/constants'

import StatusLabel from '../StatusLabel'

const renderStatusLabel = (status: string) => {
  return render(<StatusLabel status={status} />)
}

describe('StatusLabel', () => {
  it('should display "expirée" if offer is expired', () => {
    renderStatusLabel(OFFER_STATUS_EXPIRED)
    expect(screen.getByText('expirée')).toBeInTheDocument()
  })
  it('should display "publiée" if offer is active', () => {
    renderStatusLabel(OFFER_STATUS_ACTIVE)
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })
  it('should display "désactivée" if offer is inactive', () => {
    renderStatusLabel(OFFER_STATUS_INACTIVE)
    expect(screen.getByText('désactivée')).toBeInTheDocument()
  })
  it('should display "en attente" if offer is pending', () => {
    renderStatusLabel(OFFER_STATUS_PENDING)
    expect(screen.getByText('en attente')).toBeInTheDocument()
  })
  it('should display "refusée" if offer is rejected', () => {
    renderStatusLabel(OFFER_STATUS_REJECTED)
    expect(screen.getByText('refusée')).toBeInTheDocument()
  })
  it('should display "épuisée" if offer is sold out', () => {
    renderStatusLabel(OFFER_STATUS_SOLD_OUT)
    expect(screen.getByText('épuisée')).toBeInTheDocument()
  })
})
