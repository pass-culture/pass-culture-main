import { screen } from '@testing-library/react'
import React from 'react'
import type { Row } from 'react-table'

import { api } from 'apiClient/api'
import {
  CancelablePromise,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import {
  collectiveBookingDetailsFactory,
  collectiveBookingRecapFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveTableRow, { ITableBodyProps } from '../CollectiveTableRow'

jest.mock('apiClient/api')
jest.mock(
  'screens/Bookings/BookingsRecapTable/components/Table/Body/TableRow/TableRow',
  () => ({
    __esModule: true,
    default: jest.fn(() => <tr />),
  })
)

const scrollIntoViewMock = jest.fn()

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn().mockReturnValue(true),
}))

const renderCollectiveTableRow = (props: ITableBodyProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <CollectiveTableRow {...props} />
      </tbody>
    </table>
  )

describe('CollectiveTableRow', () => {
  beforeAll(() => {
    window.matchMedia = jest.fn().mockReturnValueOnce({ matches: true })

    jest
      .spyOn(api, 'getCollectiveBookingById')
      .mockResolvedValue(collectiveBookingDetailsFactory())
  })

  it('should not render booking details if row is not expanded', async () => {
    const row = {
      original: {
        bookingIdentifier: 'A1',
        stock: {
          offerIdentifier: 'A1',
        },
        bookingStatus: 'booked',
      },
      isExpanded: false,
    } as Row<CollectiveBookingResponseModel>

    renderCollectiveTableRow({ row, reloadBookings: jest.fn(), bookingId: '' })

    expect(
      screen.queryByText('Métier Alexandre Bérard')
    ).not.toBeInTheDocument()
  })

  it('should render loader while fetching data', async () => {
    const row = {
      original: {
        bookingIdentifier: 'A1',
        stock: {
          offerIdentifier: 'A1',
        },
        bookingStatus: 'booked',
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

    renderCollectiveTableRow({ row, reloadBookings: jest.fn(), bookingId: '' })

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display booking details if row is expanded', async () => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const row = {
      original: { ...collectiveBookingRecapFactory({ bookingId: '123' }) },
      isExpanded: true,
      toggleRowExpanded: () => {
        jest.fn()
      },
    } as Row<CollectiveBookingResponseModel>

    renderCollectiveTableRow({
      row,
      reloadBookings: jest.fn(),
      bookingId: '123',
    })
    expect(api.getCollectiveBookingById).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('Contact de l’établissement scolaire')
    ).toBeInTheDocument()
  })
})
