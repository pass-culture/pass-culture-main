import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import {
  OffersSynchronization,
  OffersSynchronizationProps,
} from 'pages/VenueSettings/VenueProvidersManager/OffersSynchronization/OffersSynchronization'

const renderComponent = (
  props: OffersSynchronizationProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<OffersSynchronization {...props} />, options)
}

describe('OffersSynchronization', () => {
  let props: OffersSynchronizationProps

  beforeEach(() => {
    props = {
      venue: defaultGetVenue,
      venueProviders: [],
    }
  })

  describe('OA feature flag', () => {
    it('should display the right wording without the OA FF', () => {
      renderComponent(props)

      expect(
        screen.getByText(/Vous pouvez synchroniser votre lieu/)
      ).toBeInTheDocument()
    })

    it('should display the right wording with the OA FF', () => {
      renderComponent(props, {
        features: ['WIP_ENABLE_OFFER_ADDRESS'],
      })

      expect(
        screen.getByText(/Vous pouvez synchroniser votre structure/)
      ).toBeInTheDocument()
    })
  })
})
