import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  CollectiveAdditionalFeeType,
  EacFormat,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { defaultAdageUser } from '@/commons/utils/factories/adageFactories'
import {
  defaultGetVenue,
  getCollectiveOfferCollectiveStockFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { AdagePreviewLayout } from '../AdagePreviewLayout'

function renderAdagePreviewLayout(
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel = getCollectiveOfferTemplateFactory(),
  options?: RenderWithProvidersOptions
) {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdagePreviewLayout offer={offer} />
    </AdageUserContextProvider>,
    options
  )
}

describe('AdagePreviewLayout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
    })
  })

  it('should show a preview of the offer template', async () => {
    renderAdagePreviewLayout({
      ...getCollectiveOfferTemplateFactory(),
      name: 'My test name',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name' })
    ).toBeInTheDocument()
  })

  it('should show a preview of the offer bookable', async () => {
    renderAdagePreviewLayout({
      ...getCollectiveOfferFactory(),
      name: 'My test name bookable',
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name bookable' })
    ).toBeInTheDocument()
  })

  it('should handle all offer input fields types', async () => {
    renderAdagePreviewLayout(
      getCollectiveOfferFactory({
        name: 'My test name bookable',
        domains: [{ id: 23, name: 'My test domain' }],
        formats: [EacFormat.ATELIER_DE_PRATIQUE],
        contactEmail: null,
      })
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'My test name bookable' })
    ).toBeVisible()
    expect(screen.getByText('My test domain')).toBeVisible()
    expect(screen.getByText(EacFormat.ATELIER_DE_PRATIQUE)).toBeVisible()
    expect(screen.queryByText('email')).not.toBeInTheDocument()
  })

  it('should handle offer price fields with WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS', async () => {
    const ffOptions: RenderWithProvidersOptions = {
      features: ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'],
    }

    renderAdagePreviewLayout(
      getCollectiveOfferFactory({
        collectiveStock: {
          ...getCollectiveOfferCollectiveStockFactory(),
          price: 120.5,
          servicePrice: 100,
          collectiveAdditionalFees: [
            {
              type: CollectiveAdditionalFeeType.MEAL,
              amount: 5,
              label: null,
            },
            {
              type: CollectiveAdditionalFeeType.OTHER,
              amount: 15.5,
              label: 'Autre frais',
            },
          ],
        },
      }),
      ffOptions
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Prix total TTC : 120,5 €/)).toBeVisible()
    expect(
      screen.getByText(/Dont le tarif de la prestation : 100 €/)
    ).toBeVisible()
    expect(screen.getByText(/Dont les frais annexes/)).toBeVisible()
    expect(screen.getByText(/Repas de l'intervenant•e : 5 €/)).toBeVisible()
    expect(screen.getByText(/Autre frais : 15,5 €/)).toBeVisible()
  })
})
