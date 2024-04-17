import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DownloadBookingsModal } from '../DownloadBookingsModal/DownloadBookingsModal'

const MOCK_OFFER_ID = 1

const render = () => {
  renderWithProviders(
    <DownloadBookingsModal offerId={MOCK_OFFER_ID} onDimiss={() => {}} />,
    { features: ['WIP_ENABLE_DOWNLOAD_BOOKINGS'] }
  )
}

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

    expect(screen)

    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format CSV' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Télécharger au format Excel' })
    ).toBeInTheDocument()
  })
})
