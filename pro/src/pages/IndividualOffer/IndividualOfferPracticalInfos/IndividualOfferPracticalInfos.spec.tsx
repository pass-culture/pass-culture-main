import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  getStocksResponseFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferPracticalInfos } from './IndividualOfferPracticalInfos'

const offer = getIndividualOfferFactory()

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useParams: () => ({
    offerId: offer.id,
  }),
}))

const renderIndividualOfferMedia = () => {
  return renderWithProviders(
    <IndividualOfferContextProvider>
      <IndividualOfferPracticalInfos />
    </IndividualOfferContextProvider>,
    { storeOverrides: { user: { currentUser: sharedCurrentUserFactory() } } }
  )
}

describe('IndividialOfferPracticalInfos', () => {
  it('should render a spinner until offer is fetched', () => {
    renderIndividualOfferMedia()

    const spinner = screen.getByTestId('spinner')
    expect(spinner).toBeInTheDocument()
  })

  it('should display the page once the offer is fetched', async () => {
    vi.spyOn(api, 'getOffer').mockResolvedValue(offer)
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getStocks').mockResolvedValue(getStocksResponseFactory({}))

    renderIndividualOfferMedia()

    const heading = await screen.findByRole('heading', {
      name: 'Informations pratiques',
    })
    expect(heading).toBeInTheDocument()
  })
})
