import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers/constants'
import { configureTestStore } from 'store/testUtils'

import StatusLabel from '../StatusLabel'

const renderStatusLabel = (status: string, store: any) => {
  return render(
    <Provider store={configureTestStore(store)}>
      <StatusLabel status={status} />
    </Provider>
  )
}

describe('StatusLabel', () => {
  let store = {}
  it('should display "expirée" if offer is expired', () => {
    renderStatusLabel(OFFER_STATUS_EXPIRED, store)
    expect(screen.getByText('expirée')).toBeInTheDocument()
  })
  it('should display "expirée" if offer is active', () => {
    renderStatusLabel(OFFER_STATUS_ACTIVE, store)
    expect(screen.getByText('active')).toBeInTheDocument()
  })
  it('should display "expirée" if offer is inactive', () => {
    renderStatusLabel(OFFER_STATUS_INACTIVE, store)
    expect(screen.getByText('désactivée')).toBeInTheDocument()
  })
  it('should display "expirée" if offer is pending', () => {
    renderStatusLabel(OFFER_STATUS_PENDING, store)
    expect(screen.getByText('en attente')).toBeInTheDocument()
  })
  it('should display "expirée" if offer is rejected', () => {
    renderStatusLabel(OFFER_STATUS_REJECTED, store)
    expect(screen.getByText('refusée')).toBeInTheDocument()
  })
  it('should display "expirée" if offer is sold out', () => {
    renderStatusLabel(OFFER_STATUS_SOLD_OUT, store)
    expect(screen.getByText('épuisée')).toBeInTheDocument()
  })

  it('should display "publiée" if offer is active with FF', () => {
    store = {
      features: {
        list: [
          {
            isActive: true,
            nameKey: 'OFFER_FORM_SUMMARY_PAGE',
          },
        ],
      },
    }
    renderStatusLabel(OFFER_STATUS_ACTIVE, store)
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })
})
