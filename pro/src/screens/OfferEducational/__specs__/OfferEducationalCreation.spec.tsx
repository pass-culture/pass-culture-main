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
import { IOfferEducationalProps } from '../OfferEducational'

jest.mock('apiClient/api', () => ({
  api: {
    editCollectiveOffer: jest.fn(),
  },
}))

jest.mock('repository/pcapi/pcapi', () => ({
  postCollectiveOfferImage: jest.fn(),
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

Element.prototype.scrollIntoView = jest.fn()

window.matchMedia = jest.fn().mockReturnValue({ matches: true })

describe('screens | OfferEducational : event address step', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>
  let offer: CollectiveOffer
  const mockNavigate = jest.fn()

  beforeEach(() => {
    offer = collectiveOfferFactory()

    offer.venue.managingOfferer.nonHumanizedId = 1

    props = {
      ...defaultCreationProps,
      offer,
    }

    jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect to stock on submit', async () => {
    jest.spyOn(patchCollectiveOfferAdapter, 'default').mockResolvedValueOnce({
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
    jest.spyOn(patchCollectiveOfferAdapter, 'default').mockResolvedValueOnce({
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
