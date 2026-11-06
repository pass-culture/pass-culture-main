import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getOfferVenueFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferTimetable } from './IndividualOfferTimetable'

vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
}))

const renderIndividualOfferTimetable = ({
  offer,
  features = [],
}: {
  offer: GetIndividualOfferResponseModel
  features?: string[]
}) => {
  vi.spyOn(api, 'getOffer').mockResolvedValue(offer)

  return renderWithProviders(
    <IndividualOfferContextProvider>
      <IndividualOfferTimetable />
    </IndividualOfferContextProvider>,
    {
      features,
      initialRouterEntries: [`/offre/${offer.id}/horaires`],
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    },
    '/offre/:offerId/horaires'
  )
}

describe('IndividualOfferTimetable', () => {
  let offer: GetIndividualOfferResponseModel
  const offerId = 12

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      id: offerId,
      venue: getOfferVenueFactory({
        departementCode: '75',
      }),
    })
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })

    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({
        stocks: [],
        totalStockCount: 0,
      })
    )
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderIndividualOfferTimetable({ offer })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the content of the offer timetable form', async () => {
    renderIndividualOfferTimetable({ offer })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('heading', { name: 'Horaires et stocks' })
    ).toBeInTheDocument()
  })

  it('should stay on page 2 after saving a stock and refreshing the offer', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    const stock = getOfferStockFactory({
      beginningDatetime: addDays(new Date(), 2).toISOString(),
      priceCategoryId: 1,
      quantity: 25,
    })
    const firstPageStocks = Array.from({ length: 20 }, () =>
      getOfferStockFactory({ quantity: 10 })
    )
    const secondPageStocks = [stock]
    const updatedSecondPageStocks = [{ ...stock, quantity: 30 }]
    const totalStockCount = firstPageStocks.length + secondPageStocks.length
    offer = {
      ...offer,
      priceCategories: [{ id: 1, hasStocks: true, label: 'Tarif 1', price: 1 }],
    }
    vi.spyOn(api, 'getStocks')
      // Initial load: fetch the first page.
      .mockResolvedValueOnce(
        getStocksResponseFactory({
          stocks: firstPageStocks,
          totalStockCount,
        })
      )
      // Pagination: fetch the second page.
      .mockResolvedValueOnce(
        getStocksResponseFactory({
          stocks: secondPageStocks,
          totalStockCount,
        })
      )
      // After saving: refresh the second page with the updated stock.
      .mockResolvedValue(
        getStocksResponseFactory({
          stocks: updatedSecondPageStocks,
          totalStockCount,
        })
      )
    vi.spyOn(api, 'bulkUpdateEventStocks').mockResolvedValue(
      getStocksResponseFactory({ editedStockCount: 1 })
    )

    renderIndividualOfferTimetable({ offer })

    await userEvent.click(
      await screen.findByRole('button', { name: /page suivante/ })
    )
    expect(await screen.findByRole('cell', { name: '25' })).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Modifier la date' })
    )
    await userEvent.clear(screen.getByLabelText('Places restantes'))
    await userEvent.type(screen.getByLabelText('Places restantes'), '30')
    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
    await waitFor(() => {
      expect(api.getOffer).toHaveBeenCalledTimes(2)
    })
    expect(
      screen.getByRole('button', { name: /Page 2 sur 2/ })
    ).toBeInTheDocument()
    expect(await screen.findByRole('cell', { name: '30' })).toBeInTheDocument()
  })
})
