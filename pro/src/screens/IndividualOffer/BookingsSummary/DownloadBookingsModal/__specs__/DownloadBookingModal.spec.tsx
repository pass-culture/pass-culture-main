import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { EventDatesInfos } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DownloadBookingsModal } from '../DownloadBookingsModal'

const MOCK_OFFER_ID = 1
const mockLogEvent = jest.fn()

const render = (priceCategoryAndScheduleCountByDate: EventDatesInfos) => {
  renderWithProviders(
    <DownloadBookingsModal
      offerId={MOCK_OFFER_ID}
      priceCategoryAndScheduleCountByDate={priceCategoryAndScheduleCountByDate}
      onDimiss={() => {}}
    />,
    { features: ['WIP_ENABLE_DOWNLOAD_BOOKINGS'] }
  )
}

vi.mock('utils/downloadFile', () => ({ downloadFile: vi.fn() }))

describe('DownloadBookingModal', () => {
  it('should display offer dates table', () => {
    render([
      {
        eventDate: '2022-01-01',
        scheduleCount: 1,
        priceCategoriesCount: 1,
      },
      {
        eventDate: '2022-01-02',
        scheduleCount: 5,
        priceCategoriesCount: 3,
      },
      {
        eventDate: '2022-01-03',
        scheduleCount: 2,
        priceCategoriesCount: 2,
      },
    ])

    expect(
      screen.getByText('Téléchargement de vos réservations')
    ).toBeInTheDocument()

    // 3 lines = 9 cells
    const tableCells = screen.getAllByRole('cell')
    expect(tableCells).toHaveLength(9)

    expect(
      tableCells.filter((cell) =>
        cell.textContent?.match(/^\w{3}\d{2}\/\d{2}\/\d{4}$/)
      )
    ).toHaveLength(3)

    expect(
      tableCells.filter((cell) => cell.textContent?.match(/^\d+ horaire[s]?$/))
    ).toHaveLength(3)

    expect(
      tableCells.filter((cell) => cell.textContent?.match(/^\d+ tarif[s]?$/))
    ).toHaveLength(3)

    const shortWeekDays = screen.getAllByTestId('short-week-day')
    expect(shortWeekDays).toHaveLength(3)
    expect(shortWeekDays[0]).toHaveTextContent('Sam')
    expect(shortWeekDays[1]).toHaveTextContent('Dim')
    expect(shortWeekDays[2]).toHaveTextContent('Lun')

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format CSV' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format Excel' })
    ).toBeInTheDocument()
  })

  it('should not display date selection table and submit should be clickable if only one date is returned', async () => {
    render([
      {
        eventDate: '2022-01-01',
        scheduleCount: 1,
        priceCategoriesCount: 1,
      },
    ])

    expect(
      screen.getByText('Téléchargement de vos réservations')
    ).toBeInTheDocument()

    expect(screen.queryByRole('cell')).not.toBeInTheDocument()

    expect(
      screen.getByText('Date de votre évènement : 01/01/2022')
    ).toBeInTheDocument()

    const allBookings = screen.getByText('Toutes les réservations')
    await userEvent.click(allBookings)

    expect(
      screen.getByRole('button', { name: 'Télécharger au format CSV' })
    ).toBeEnabled()
  })

  it('should download validated bookings as CSV', async () => {
    vi.spyOn(api, 'exportBookingsForOfferAsCsv').mockResolvedValueOnce('')
    vi.spyOn(useAnalytics, 'default').mockReturnValue({
      logEvent: mockLogEvent,
    })

    render([
      {
        eventDate: '2022-01-01',
        scheduleCount: 1,
        priceCategoriesCount: 1,
      },
      {
        eventDate: '2022-01-02',
        scheduleCount: 5,
        priceCategoriesCount: 3,
      },
      {
        eventDate: '2022-01-03',
        scheduleCount: 2,
        priceCategoriesCount: 2,
      },
    ])

    expect(
      screen.getByText('Téléchargement de vos réservations')
    ).toBeInTheDocument()

    // 3 lines = 9 cells
    const tableCells = screen.getAllByRole('cell')
    expect(tableCells).toHaveLength(9)

    const eventDate = screen.getByText('01/01/2022')
    await userEvent.click(eventDate)

    const validatedBookings = screen.getByText(
      'Réservations confirmées et validées uniquement'
    )
    await userEvent.click(validatedBookings)
    const downLoadCsvButton = screen.getByRole('button', {
      name: 'Télécharger au format CSV',
    })

    await userEvent.click(downLoadCsvButton)
    expect(api.exportBookingsForOfferAsCsv).toBeCalledWith(
      MOCK_OFFER_ID,
      'validated',
      '2022-01-01'
    )

    expect(mockLogEvent).toBeCalledWith('hasDownloadedBookings', {
      format: 'csv',
      bookingStatus: 'validated',
      offerId: MOCK_OFFER_ID,
    })
  })

  it('should download all bookings as Excel', async () => {
    vi.spyOn(api, 'exportBookingsForOfferAsExcel').mockResolvedValueOnce({})
    vi.spyOn(useAnalytics, 'default').mockReturnValue({
      logEvent: mockLogEvent,
    })

    render([
      {
        eventDate: '2022-01-01',
        scheduleCount: 1,
        priceCategoriesCount: 1,
      },
      {
        eventDate: '2022-01-02',
        scheduleCount: 5,
        priceCategoriesCount: 3,
      },
      {
        eventDate: '2022-01-03',
        scheduleCount: 2,
        priceCategoriesCount: 2,
      },
    ])

    expect(
      screen.getByText('Téléchargement de vos réservations')
    ).toBeInTheDocument()

    // 3 lines = 9 cells
    const tableCells = screen.getAllByRole('cell')
    expect(tableCells).toHaveLength(9)

    const eventDate = screen.getByText(/02\/01\/2022/)
    await userEvent.click(eventDate)

    const allBookings = screen.getByText('Toutes les réservations')
    await userEvent.click(allBookings)

    const downLoadXlsxButton = screen.getByRole('button', {
      name: 'Télécharger au format Excel',
    })

    await userEvent.click(downLoadXlsxButton)
    expect(api.exportBookingsForOfferAsExcel).toBeCalledWith(
      MOCK_OFFER_ID,
      'all',
      '2022-01-02'
    )

    expect(mockLogEvent).toBeCalledWith('hasDownloadedBookings', {
      format: 'excel',
      bookingStatus: 'all',
      offerId: MOCK_OFFER_ID,
    })
  })
})
