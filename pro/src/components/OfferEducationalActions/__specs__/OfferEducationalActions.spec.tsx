import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { CollectiveBookingStatus, OfferStatus } from 'apiClient/v1'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import OfferEducationalActions, {
  IOfferEducationalActions,
} from '../OfferEducationalActions'

const renderOfferEducationalActions = (
  props: IOfferEducationalActions,
  storeOverride?: Partial<RootState>
) => {
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    features: {
      initialized: true,
      list: [
        {
          isActive: true,
          nameKey: 'WIP_IMPROVE_COLLECTIVE_STATUS',
        },
      ],
    },
    ...storeOverride,
  })
  return render(
    <MemoryRouter>
      <Provider store={store}>
        <OfferEducationalActions {...props} />
      </Provider>
    </MemoryRouter>
  )
}

describe('OfferEducationalActions', () => {
  let props: IOfferEducationalActions
  beforeEach(() => {
    props = {
      className: 'string',
      isOfferActive: true,
      isBooked: false,
      offer: collectiveOfferFactory(),
      setIsOfferActive: jest.fn(),
      cancelActiveBookings: jest.fn(),
    }
  })

  it('should display actions button and status tag by default', () => {
    renderOfferEducationalActions(props)
    expect(
      screen.getByRole('button', { name: 'Masquer la publication sur Adage' })
    ).toBeInTheDocument()
    expect(screen.getByText('publiée')).toBeInTheDocument()
  })

  it('should display booking link for booked offer', () => {
    props.offer = collectiveOfferFactory({
      status: OfferStatus.SOLD_OUT,
      lastBookingId: 1,
      lastBookingStatus: CollectiveBookingStatus.CONFIRMED,
    })
    const storeOverride = {}
    renderOfferEducationalActions(props, storeOverride)
    expect(
      screen.getByRole('link', { name: 'Voir la réservation' })
    ).toHaveAttribute(
      'href',
      '/reservations/collectives?page=1&offerEventDate=2021-10-15&bookingStatusFilter=booked&offerType=all&offerVenueId=all&bookingId=1'
    )
    expect(screen.getByText('réservée')).toBeInTheDocument()
  })
  it('should display cancel booking button if offer is cancelable', () => {
    const storeOverride = {
      features: {
        initialized: true,
        list: [
          {
            isActive: false,
            nameKey: 'WIP_IMPROVE_COLLECTIVE_STATUS',
          },
        ],
      },
    }
    props.isBooked = true
    renderOfferEducationalActions(props, storeOverride)
    expect(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    ).toBeInTheDocument()
  })
  it('should open confirm modal when clicking cancel booking button and cancel booking on confirm', async () => {
    const storeOverride = {
      features: {
        initialized: true,
        list: [
          {
            isActive: false,
            nameKey: 'WIP_IMPROVE_COLLECTIVE_STATUS',
          },
        ],
      },
    }
    props.isBooked = true
    renderOfferEducationalActions(props, storeOverride)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Annuler la réservation',
      })
    )
    expect(
      screen.getByText(
        'L’établissement scolaire concerné recevra un message lui indiquant l’annulation de sa réservation.'
      )
    ).toBeInTheDocument()
  })
})
