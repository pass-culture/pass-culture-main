import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferMedia } from './IndividualOfferMedia'

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
      <IndividualOfferMedia />
    </IndividualOfferContextProvider>,
    { storeOverrides: {} }
  )
}

describe('IndividialOfferMedia', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValue(offer)
  })

  it('should render a spinner until offer is fetched', async () => {
    renderIndividualOfferMedia()

    await waitFor(() => {
      expect(screen.getByTestId('spinner')).toBeInTheDocument()
    })
  })

  it('should display the page once the offer is fetched', async () => {
    renderIndividualOfferMedia()

    const heading = await screen.findByRole('heading', {
      name: 'Illustrez votre offre',
    })
    expect(heading).toBeInTheDocument()
  })
})
