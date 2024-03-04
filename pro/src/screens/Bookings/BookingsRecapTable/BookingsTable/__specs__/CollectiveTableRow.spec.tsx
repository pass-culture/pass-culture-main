import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CancelablePromise,
  CollectiveBookingByIdResponseModel,
} from 'apiClient/v1'
import {
  collectiveBookingCollectiveStockFactory,
  collectiveBookingByIdFactory,
  collectiveBookingFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CollectiveTableRow,
  CollectiveTableRowProps,
} from '../CollectiveTableRow'

vi.mock('apiClient/api')
vi.mock(
  'screens/Bookings/BookingsRecapTable/components/Table/Body/TableRow/TableRow',
  () => ({
    __esModule: true,
    default: vi.fn(() => <tr />),
  })
)

const scrollIntoViewMock = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

const renderCollectiveTableRow = (props: CollectiveTableRowProps) =>
  renderWithProviders(
    <table>
      <tbody>
        <CollectiveTableRow {...props} />
      </tbody>
    </table>
  )

describe('CollectiveTableRow', () => {
  beforeEach(() => {
    vi.spyOn(window, 'matchMedia').mockReturnValue({
      matches: true,
    } as MediaQueryList)

    vi.spyOn(api, 'getCollectiveBookingById').mockResolvedValue(
      collectiveBookingByIdFactory()
    )
  })

  it('should not render booking details if row is not expanded', () => {
    const props: CollectiveTableRowProps = {
      booking: collectiveBookingFactory({
        stock: collectiveBookingCollectiveStockFactory(),
        bookingStatus: 'booked',
      }),
      reloadBookings: vi.fn(),
      defaultOpenedBookingId: '',
    }

    renderCollectiveTableRow(props)

    expect(
      screen.queryByText('Métier Alexandre Bérard')
    ).not.toBeInTheDocument()
  })

  it('should render loader while fetching data', async () => {
    const props: CollectiveTableRowProps = {
      booking: collectiveBookingFactory({
        stock: collectiveBookingCollectiveStockFactory(),
        bookingStatus: 'booked',
      }),
      reloadBookings: vi.fn(),
      defaultOpenedBookingId: '',
    }

    vi.spyOn(api, 'getCollectiveBookingById').mockImplementationOnce(() => {
      return new CancelablePromise<CollectiveBookingByIdResponseModel>(
        (resolve) =>
          setTimeout(() => resolve(collectiveBookingByIdFactory()), 500)
      )
    })

    renderCollectiveTableRow(props)

    await userEvent.click(screen.getByText(/Détails/))

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should display booking details if row is expanded', async () => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const props: CollectiveTableRowProps = {
      booking: collectiveBookingFactory({ bookingId: '123' }),
      reloadBookings: vi.fn(),
      defaultOpenedBookingId: '123',
    }

    renderCollectiveTableRow(props)
    expect(api.getCollectiveBookingById).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('Contact de l’établissement scolaire')
    ).toBeInTheDocument()
  })
})
