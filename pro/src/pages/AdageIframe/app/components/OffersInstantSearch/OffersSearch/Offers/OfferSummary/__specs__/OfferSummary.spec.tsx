import { screen } from '@testing-library/react'
import React from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { OfferSummary, OfferSummaryProps } from '../OfferSummary'

const renderOfferSummary = (
  props: OfferSummaryProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<OfferSummary {...props} />, options)
}

describe('offer summary', () => {
  it('should show the dates range of a template offers', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...defaultCollectiveTemplateOffer,
      dates: { start: '2023-10-24T00:00:00Z', end: '2023-10-24T23:59:00Z' },
      isTemplate: true,
    }
    renderOfferSummary({ offer })
    expect(screen.getByText('Le mardi 24 octobre 2023')).toBeInTheDocument()
  })

  it('should not show the dates range on template offers if the dates are not defined', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...defaultCollectiveTemplateOffer,
      dates: undefined,
      isTemplate: true,
    }
    renderOfferSummary({ offer })
    expect(
      screen.queryByText('Le mardi 24 octobre 2023')
    ).not.toBeInTheDocument()
  })

  it('should show that the offer is permanent when there are no dates on a template offer', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...defaultCollectiveTemplateOffer,
      dates: undefined,
      isTemplate: true,
    }
    renderOfferSummary({ offer })
    expect(
      screen.queryByText(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    ).toBeInTheDocument()
  })
})
