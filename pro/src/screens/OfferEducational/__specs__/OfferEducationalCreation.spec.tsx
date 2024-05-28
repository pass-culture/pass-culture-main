import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { RootState } from 'store/rootReducer'
import { getCollectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

vi.mock('apiClient/api', () => ({
  api: {
    editCollectiveOffer: vi.fn(),
  },
}))

vi.mock('repository/pcapi/pcapi', () => ({
  postCollectiveOfferImage: vi.fn(),
}))

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps
  let store: Partial<RootState>
  let offer: GetCollectiveOfferResponseModel
  const mockNavigate = vi.fn()

  beforeEach(() => {
    offer = getCollectiveOfferFactory()

    offer.venue.managingOfferer.id = 1

    props = {
      ...defaultCreationProps,
      offer,
    }

    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect to stock on submit', async () => {
    vi.spyOn(api, 'editCollectiveOffer').mockResolvedValueOnce(offer)

    renderWithProviders(<OfferEducational {...props} />)

    const buttonNextStep = screen.getByText('Étape suivante')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith('/offre/2/collectif/stocks')
  })

  it('should redirect to right url if requete params exist on submit', async () => {
    vi.spyOn(api, 'editCollectiveOffer').mockResolvedValueOnce(offer)

    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: store,
      initialRouterEntries: ['/offre/collectif/3/creation?requete=1'],
    })

    const buttonNextStep = screen.getByText('Étape suivante')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/3/collectif/stocks?requete=1'
    )
  })
})
