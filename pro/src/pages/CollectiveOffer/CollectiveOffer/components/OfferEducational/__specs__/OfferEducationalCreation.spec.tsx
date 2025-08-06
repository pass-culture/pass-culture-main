import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  GetCollectiveOfferResponseModel,
} from '@/apiClient/v1'
import * as useOfferer from '@/commons/hooks/swr/useOfferer'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

vi.mock('@/apiClient/api', () => ({
  api: {
    editCollectiveOffer: vi.fn(),
    getVenues: vi.fn(),
  },
}))

vi.mock('repository/pcapi/pcapi', () => ({
  postCollectiveOfferImage: vi.fn(),
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

function renderComponent(props: OfferEducationalProps, route?: string) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
    initialRouterEntries: route ? [route] : undefined,
  })
}

// TODO (ahello - 17/03/25) this test should really test offer creation (should not have an offer in its props)
describe('screens | OfferEducational : creation', () => {
  let props: OfferEducationalProps
  let offer: GetCollectiveOfferResponseModel
  const mockNavigate = vi.fn()

  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  beforeEach(() => {
    offer = getCollectiveOfferFactory()

    offer.venue.managingOfferer.id = 1
    offer.allowedActions = [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS]

    props = {
      ...defaultCreationProps,
      offer,
    }

    vi.spyOn(useOfferer, 'useOfferer').mockReturnValue(mockOffererData)
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect to stock on submit', async () => {
    vi.spyOn(api, 'editCollectiveOffer').mockResolvedValueOnce(offer)
    renderComponent(props)
    const buttonNextStep = screen.getByText('Enregistrer et continuer')

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith('/offre/2/collectif/stocks')
  })

  it('should redirect to right url if requete params exist on submit', async () => {
    vi.spyOn(api, 'editCollectiveOffer').mockResolvedValueOnce(offer)
    renderComponent(props, '/offre/collectif/3/creation?requete=1')

    const buttonNextStep = screen.getByText('Enregistrer et continuer')

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/3/collectif/stocks?requete=1'
    )
  })
})
