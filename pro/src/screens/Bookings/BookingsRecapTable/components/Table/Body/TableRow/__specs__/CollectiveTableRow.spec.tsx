import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import type { Row } from 'react-table'

import { api } from 'apiClient/api'
import {
  CancelablePromise,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'

import CollectiveTableRow, { ITableBodyProps } from '../CollectiveTableRow'

jest.mock('apiClient/api')
jest.mock(
  'screens/Bookings/BookingsRecapTable/components/Table/Body/TableRow/TableRow',
  () => ({
    __esModule: true,
    default: jest.fn(() => <tr />),
  })
)

const renderCollectiveTableRow = (props: ITableBodyProps) =>
  render(
    <Router history={createBrowserHistory()}>
      <Provider store={configureTestStore({})}>
        <CollectiveTableRow {...props} />
      </Provider>
    </Router>
  )

describe('CollectiveTableRow', () => {
  beforeAll(() => {
    jest.spyOn(api, 'getCollectiveBookingById').mockResolvedValue({
      id: 1,
      beginningDatetime: new Date('2022-01-23T10:30:00').toISOString(),
      venuePostalCode: '75017',
      offerVenue: {
        addressType: OfferAddressType.OFFERER_VENUE,
        otherAddress: '',
        venueId: 'V1',
      },
      numberOfTickets: 10,
      price: 0,
      students: [StudentLevels.COLL_GE_4E],
      educationalInstitution: {
        institutionType: 'LYCEE PROFESIONNEL',
        name: 'Métier Alexandre Bérard',
        postalCode: '01500',
        city: 'Ambérieu-en-Buguey',
        id: 1,
        phoneNumber: '0672930477',
      },
      educationalRedactor: {
        firstName: 'Benoit',
        lastName: 'Demon',
        email: 'benoit.demon@lyc-alexandreberard.com',
        civility: 'M',
        id: 1,
      },
    })
  })

  it('should not render booking details if row is not expanded', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
        stock: {
          offer_identifier: 'A1',
        },
      },
      isExpanded: false,
    } as Row<CollectiveBookingResponseModel>

    renderCollectiveTableRow({ row, reloadBookings: jest.fn() })

    expect(
      screen.queryByText('Métier Alexandre Bérard')
    ).not.toBeInTheDocument()
  })

  it('should render loader while fetching data', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
        stock: {
          offer_identifier: 'A1',
        },
      },
      isExpanded: true,
    } as Row<CollectiveBookingResponseModel>

    jest
      .spyOn(api, 'getCollectiveBookingById')
      .mockResolvedValueOnce(
        new CancelablePromise(resolve =>
          setTimeout(
            () => resolve({} as CollectiveBookingByIdResponseModel),
            500
          )
        )
      )

    renderCollectiveTableRow({ row, reloadBookings: jest.fn() })

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display booking details if row is expanded', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
        stock: {
          offer_identifier: 'A1',
        },
      },
      isExpanded: true,
    } as Row<CollectiveBookingResponseModel>

    renderCollectiveTableRow({ row, reloadBookings: jest.fn() })

    expect(await screen.findByText('10 élèves')).toBeInTheDocument()
    expect(await screen.findByText('0€')).toBeInTheDocument()
    expect(await screen.findByText('Collège - 4e')).toBeInTheDocument()
    expect(
      await screen.findByText('LYCEE PROFESIONNEL Métier Alexandre Bérard', {
        exact: false,
      })
    ).toBeInTheDocument()
  })

  it('should reload bookings after cancelling one', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
        stock: {
          offer_identifier: 'A1',
        },
      },
      isExpanded: true,
    } as Row<CollectiveBookingResponseModel>
    const reloadBookings = jest.fn()

    renderCollectiveTableRow({ row, reloadBookings })

    expect(await screen.findByText('10 élèves')).toBeInTheDocument()
    await userEvent.click(
      await screen.findByRole('button', { name: 'Annuler la réservation' })
    )
    expect(reloadBookings).toHaveBeenCalledTimes(1)
  })
})
