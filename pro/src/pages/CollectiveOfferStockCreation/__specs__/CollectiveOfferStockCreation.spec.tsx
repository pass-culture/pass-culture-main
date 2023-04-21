import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import * as useNotification from 'hooks/useNotification'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { dehumanizeId } from 'utils/dehumanize'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferStockCreation } from '../CollectiveOfferStockCreation'

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

const renderCollectiveStockCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferStockCreation {...props} />, {
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: collectiveOfferFactory(),
  setOffer: jest.fn(),
  reloadCollectiveOffer: jest.fn(),
  isTemplate: false,
}

describe('CollectiveOfferStockCreation', () => {
  it('should render collective offer stock form', async () => {
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', defaultProps)

    expect(
      await screen.findByRole('heading', {
        name: 'Créer une nouvelle offre collective',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Date et prix',
      })
    ).toBeInTheDocument()
  })

  it('should render collective offer stock form from template', async () => {
    const props = {
      ...defaultProps,
      offer: { ...defaultProps.offer, templateId: 'FM' },
    }
    const offerTemplate = collectiveOfferTemplateFactory({
      educationalPriceDetail: 'Details from template',
    })
    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValue(offerTemplate)
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', props)
    await waitFor(() => {
      expect(api.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    })
  })

  it('should failed render collective offer stock form from template', async () => {
    const props = {
      ...defaultProps,
      offer: { ...defaultProps.offer, templateId: 'FM' },
    }
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValue({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })
    const notifyError = jest.fn()
    // @ts-expect-error
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', props)
    expect(
      await screen.findByRole('heading', {
        name: 'Créer une offre pour un établissement scolaire',
      })
    ).toBeInTheDocument()

    const response = await getCollectiveOfferTemplateAdapter(
      dehumanizeId(props.offer.templateId) || 0
    )
    expect(response.isOk).toBeFalsy()
    await waitFor(() => {
      expect(notifyError).toHaveBeenCalledTimes(1)
    })
  })
})
