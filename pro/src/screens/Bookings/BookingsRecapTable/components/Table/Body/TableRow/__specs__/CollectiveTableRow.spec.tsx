import { render, screen } from '@testing-library/react'
import { Row } from 'react-table'
import '@testing-library/jest-dom'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CancelablePromise,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'

import CollectiveTableRow from '../CollectiveTableRow'

jest.mock('apiClient/api')
jest.mock(
  'screens/Bookings/BookingsRecapTable/components/Table/Body/TableRow/TableRow',
  () => ({
    __esModule: true,
    default: jest.fn(() => <tr />),
  })
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
      },
      isExpanded: false,
    } as Row<CollectiveBookingResponseModel>

    render(<CollectiveTableRow row={row} />)

    expect(
      screen.queryByText('Métier Alexandre Bérard')
    ).not.toBeInTheDocument()
  })

  it('should render loader while fetching data', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
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

    render(<CollectiveTableRow row={row} />)
    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display booking details if row is expanded', async () => {
    const row = {
      original: {
        booking_identifier: 'A1',
      },
      isExpanded: true,
    } as Row<CollectiveBookingResponseModel>

    render(<CollectiveTableRow row={row} />)

    expect(await screen.findByText('10 élèves')).toBeInTheDocument()
    expect(await screen.findByText('0€')).toBeInTheDocument()
    expect(await screen.findByText('Collège - 4e')).toBeInTheDocument()
    expect(
      await screen.findByText('LYCEE PROFESIONNEL Métier Alexandre Bérard', {
        exact: false,
      })
    ).toBeInTheDocument()
  })
})
