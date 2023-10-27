import { screen } from '@testing-library/react'
import React from 'react'

import { HydratedCollectiveOfferTemplate } from 'pages/AdageIframe/app/types/offers'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferSummary, { OfferSummaryProps } from '../OfferSummary'

const renderOfferSummary = (props: OfferSummaryProps, storeOverrides?: any) => {
  renderWithProviders(<OfferSummary {...props} />, { storeOverrides })
}

describe('offer summary', () => {
  it('should not show the dates range on template offers if the FF is disabled', () => {
    const offer: HydratedCollectiveOfferTemplate = {
      ...defaultCollectiveTemplateOffer,
      dates: { start: '2023-10-24T00:00:00', end: '2023-10-24T23:59:00' },
      isTemplate: true,
    }
    renderOfferSummary({ offer })
    expect(
      screen.queryByText('Le mardi 24 octobre 2023')
    ).not.toBeInTheDocument()
  })

  it('should show the dates range on template offers if the FF is enabled', () => {
    const offer: HydratedCollectiveOfferTemplate = {
      ...defaultCollectiveTemplateOffer,
      dates: { start: '2023-10-24T00:00:00', end: '2023-10-24T23:59:00' },
      isTemplate: true,
    }
    renderOfferSummary(
      { offer },
      {
        features: {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_DATES_OFFER_TEMPLATE' },
          ],
        },
      }
    )
    expect(screen.queryByText('Le mardi 24 octobre 2023')).toBeInTheDocument()
  })

  it('should not show the dates range on template offers if the dates are not defined', () => {
    const offer: HydratedCollectiveOfferTemplate = {
      ...defaultCollectiveTemplateOffer,
      dates: undefined,
      isTemplate: true,
    }
    renderOfferSummary(
      { offer },
      {
        features: {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_DATES_OFFER_TEMPLATE' },
          ],
        },
      }
    )
    expect(
      screen.queryByText('Le mardi 24 octobre 2023')
    ).not.toBeInTheDocument()
  })
})
