import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { getCollectiveOfferFactory } from 'commons/utils/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'

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

vi.mock('commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

function renderComponent(props: OfferEducationalProps, route?: string) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        selectedOffererId: 1,
        currentUser: user,
      },
    },
    initialRouterEntries: route ? [route] : undefined,
  })
}

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps
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
    renderComponent(props)
    const buttonNextStep = screen.getByText('Enregistrer et continuer')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith('/offre/2/collectif/stocks')
  })

  it('should redirect to right url if requete params exist on submit', async () => {
    vi.spyOn(api, 'editCollectiveOffer').mockResolvedValueOnce(offer)
    renderComponent(props, '/offre/collectif/3/creation?requete=1')

    const buttonNextStep = screen.getByText('Enregistrer et continuer')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/3/collectif/stocks?requete=1'
    )
  })
})
