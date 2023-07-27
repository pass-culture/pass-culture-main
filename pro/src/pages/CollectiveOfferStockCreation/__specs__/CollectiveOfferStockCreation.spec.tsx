import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import * as useNotification from 'hooks/useNotification'
import getOfferRequestInformationsAdapter from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferStockCreation } from '../CollectiveOfferStockCreation'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
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
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
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
      offer: { ...defaultProps.offer, templateId: 12 },
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
      offer: { ...defaultProps.offer, templateId: 12 },
    }
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValue({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })
    const notifyError = vi.fn()
    // @ts-expect-error
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    renderCollectiveStockCreation('/offre/A1/collectif/stocks', props)
    expect(
      await screen.findByRole('heading', {
        name: 'Créer une offre pour un établissement scolaire',
      })
    ).toBeInTheDocument()

    const response = await getCollectiveOfferTemplateAdapter(
      props.offer.templateId
    )
    expect(response.isOk).toBeFalsy()
    await waitFor(() => {
      expect(notifyError).toHaveBeenCalledTimes(1)
    })
  })

  it('should render collective offer stock form from requested offer', async () => {
    const offerTemplate = collectiveOfferTemplateFactory({
      educationalPriceDetail: 'Details from template',
    })
    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValue(offerTemplate)
    renderCollectiveStockCreation(
      '/offre/A1/collectif/stocks?requete=1',
      defaultProps
    )
    await waitFor(() => {
      expect(api.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)
    })
  })

  it('should render collective offer stock form from requested offer failed', async () => {
    const notifyError = vi.fn()
    // @ts-expect-error
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))

    vi.spyOn(api, 'getCollectiveOfferRequest').mockRejectedValue({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })

    renderCollectiveStockCreation(
      '/offre/A1/collectif/stocks?requete=1',
      defaultProps
    )

    const response = await getOfferRequestInformationsAdapter(1)
    expect(response.isOk).toBeFalsy()
    await waitFor(() => {
      expect(notifyError).toHaveBeenCalledTimes(1)
    })
  })
})
