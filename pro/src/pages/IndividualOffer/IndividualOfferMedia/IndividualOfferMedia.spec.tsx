import { screen } from '@testing-library/react'

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
    </IndividualOfferContextProvider>
  )
}

describe('IndividialOfferMedia', () => {
  it('should render a spinner until offer is fetched', () => {
    renderIndividualOfferMedia()

    const spinner = screen.getByTestId('spinner')
    expect(spinner).toBeInTheDocument()
  })

  it('should display the page once the offer is fetched', async () => {
    vi.spyOn(api, 'getOffer').mockResolvedValue(offer)

    renderIndividualOfferMedia()

    const heading = await screen.findByRole('heading', {
      name: 'Illustrez votre offre',
    })
    expect(heading).toBeInTheDocument()
  })
})
