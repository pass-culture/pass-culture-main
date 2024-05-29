import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { OfferAddressType } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import * as getInterventionAreaLabels from 'pages/AdageIframe/app/components/OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferInterventionArea'
import {
  getCollectiveOfferTemplateFactory,
  defaultGetVenue,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferLocationSection } from '../CollectiveOfferLocationSection'
import * as formatOfferEventAddress from '../utils/formatOfferEventAddress'

vi.mock('apiClient/api', () => ({
  api: {
    getVenue: vi.fn(),
  },
}))

describe('CollectiveOfferLocationSection', () => {
  const notifyError = vi.fn()

  beforeEach(async () => {
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
    })

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
  })

  it('should display the location details for an event at the school', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          offerVenue: {
            ...offer.venue,
            addressType: OfferAddressType.SCHOOL,
            otherAddress: '',
          },
        }}
      />
    )

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(await screen.findByText('Lieu de l’évènement')).toBeInTheDocument()
    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should display the location details for an event in a specific location', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          offerVenue: {
            ...offer.venue,
            addressType: OfferAddressType.OTHER,
            otherAddress: 'Other address detail',
          },
        }}
      />
    )

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(screen.getByText('Other address detail')).toBeInTheDocument()
  })

  it('should display the location details for an event at the offerer venue', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          offerVenue: {
            ...offer.venue,
            addressType: OfferAddressType.OFFERER_VENUE,
            otherAddress: '',
          },
        }}
      />
    )

    vi.spyOn(
      formatOfferEventAddress,
      'formatOfferEventAddress'
    ).mockImplementationOnce(() => 'Musée, 12 rue de Rennes, 75000, Paris')

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByText('Musée, 12 rue de Rennes, 75000, Paris')
    ).toBeInTheDocument()
  })

  it('should display the mobility zone for an event', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    renderWithProviders(
      <CollectiveOfferLocationSection
        offer={{
          ...offer,
          offerVenue: {
            ...offer.venue,
            addressType: OfferAddressType.OFFERER_VENUE,
            otherAddress: '',
          },
        }}
      />
    )

    vi.spyOn(
      getInterventionAreaLabels,
      'getInterventionAreaLabels'
    ).mockImplementationOnce(
      () => '02 - Aisne, 03 - Allier, 04 - Alpes-de-Haute-Provence'
    )

    const loadingMessage = screen.queryByText(/Chargement en cours/)
    await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

    expect(
      screen.getByText('02 - Aisne, 03 - Allier, 04 - Alpes-de-Haute-Provence')
    ).toBeInTheDocument()
  })
})
