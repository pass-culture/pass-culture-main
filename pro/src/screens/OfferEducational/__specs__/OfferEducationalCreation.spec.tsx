import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'

import { CollectiveOffer } from 'core/OfferEducational'
import * as patchCollectiveOfferAdapter from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import { RootState } from 'store/reducers'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducational from '../'
import { defaultCreationProps } from '../__tests-utils__'
import { OfferEducationalProps } from '../OfferEducational'

vi.mock('apiClient/api', () => ({
  api: {
    editCollectiveOffer: vi.fn(),
  },
}))

vi.mock('repository/pcapi/pcapi', () => ({
  postCollectiveOfferImage: vi.fn(),
}))

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps
  let store: Partial<RootState>
  let offer: CollectiveOffer
  const mockNavigate = vi.fn()

  beforeEach(() => {
    offer = collectiveOfferFactory()

    offer.venue.managingOfferer.id = 1

    props = {
      ...defaultCreationProps,
      offer,
    }

    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect to stock on submit', async () => {
    vi.spyOn(patchCollectiveOfferAdapter, 'default').mockResolvedValueOnce({
      isOk: true,
      message: '',
      payload: offer,
    })

    renderWithProviders(<OfferEducational {...props} />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const buttonNextStep = screen.getByText('Étape suivante')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith('/offre/2/collectif/stocks')
  })

  it('should redirect to right url if requete params exist on submit', async () => {
    vi.spyOn(patchCollectiveOfferAdapter, 'default').mockResolvedValueOnce({
      isOk: true,
      message: '',
      payload: offer,
    })

    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: store,
      initialRouterEntries: ['/offre/collectif/3/creation?requete=1'],
    })

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const buttonNextStep = screen.getByText('Étape suivante')

    expect(buttonNextStep).toBeInTheDocument()

    await userEvent.click(buttonNextStep)

    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/3/collectif/stocks?requete=1'
    )
  })
})
