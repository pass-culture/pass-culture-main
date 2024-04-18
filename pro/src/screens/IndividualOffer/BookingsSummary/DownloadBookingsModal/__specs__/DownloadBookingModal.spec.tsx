import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DownloadBookingsModal } from '../DownloadBookingsModal'

const MOCK_OFFER_ID = 1

const render = () => {
  renderWithProviders(
    <DownloadBookingsModal offerId={MOCK_OFFER_ID} onDimiss={() => {}} />,
    { features: ['WIP_ENABLE_DOWNLOAD_BOOKINGS'] }
  )
}

vi.mock('utils/downloadFile', () => ({ downloadFile: vi.fn() }))

describe('DownloadBookingModal', () => {
  it('should display offer dates table', async () => {
    vi.spyOn(
      api,
      'getOfferPriceCategoriesAndSchedulesByDates'
    ).mockResolvedValueOnce([
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

    render()

    expect(screen.getByText('Télécharger vos réservations')).toBeInTheDocument()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

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

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format CSV' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format Excel' })
    ).toBeInTheDocument()
  })

  it('should download validated bookings as CSV', async () => {
    vi.spyOn(
      api,
      'getOfferPriceCategoriesAndSchedulesByDates'
    ).mockResolvedValueOnce([
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

    vi.spyOn(api, 'exportBookingsForOfferAsCsv').mockResolvedValueOnce('')

    render()

    expect(screen.getByText('Télécharger vos réservations')).toBeInTheDocument()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

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
  })

  it('should download all bookings as Excel', async () => {
    vi.spyOn(
      api,
      'getOfferPriceCategoriesAndSchedulesByDates'
    ).mockResolvedValueOnce([
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
    vi.spyOn(api, 'exportBookingsForOfferAsExcel').mockResolvedValueOnce({})

    render()

    expect(screen.getByText('Télécharger vos réservations')).toBeInTheDocument()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

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
  })
})
