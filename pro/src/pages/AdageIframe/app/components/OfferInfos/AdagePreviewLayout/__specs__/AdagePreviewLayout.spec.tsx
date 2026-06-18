import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  EacFormat,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { defaultAdageUser } from '@/commons/utils/factories/adageFactories'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { AdagePreviewLayout } from '../AdagePreviewLayout'

function renderAdagePreviewLayout(
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel = getCollectiveOfferTemplateFactory()
) {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdagePreviewLayout offer={offer} />
    </AdageUserContextProvider>
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
})
