import { render, screen } from '@testing-library/react'
import React from 'react'

import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'

import { DEFAULT_RECAP_VALUE } from '../../constants'
import CollectiveOfferArtisticSection from '../CollectiveOfferArtisticSection'

describe('CollectiveOfferArtisticSection', () => {
  it('should display the description', () => {
    render(
      <CollectiveOfferArtisticSection
        offer={{
          ...collectiveOfferTemplateFactory(),
        }}
      />
    )
    expect(screen.getByText('Description :')).toBeInTheDocument()
  })

  it('should display the default description if the offer description is empty', () => {
    render(
      <CollectiveOfferArtisticSection
        offer={{
          ...collectiveOfferTemplateFactory(),
          description: '',
          durationMinutes: 100,
        }}
      />
    )
    expect(screen.getByText(DEFAULT_RECAP_VALUE)).toBeInTheDocument()
  })
})
