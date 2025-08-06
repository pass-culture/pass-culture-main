import { screen } from '@testing-library/react'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Venue, VenueProps } from '../Venue'

const renderVenue = (
  props: VenueProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<Venue {...props} />, options)
}

describe('venues', () => {
  let props: VenueProps
  const offererId = 12
  const venueId = 1

  beforeEach(() => {
    props = {
      offerer: { ...defaultGetOffererResponseModel, id: offererId },
      venue: {
        ...defaultGetOffererVenueResponseModel,
        id: venueId,
        name: 'My venue',
        isVirtual: false,
      },
      isFirstVenue: false,
    }
  })

  describe('physical venue section', () => {
    it('should display edition venue link', () => {
      props.venue.isVirtual = false

      renderVenue(props)

      expect(
        screen.getByRole('link', { name: `Gérer la page de My venue` })
      ).toHaveAttribute('href', `/structures/${offererId}/lieux/${venueId}`)
    })
  })

  it('should not display dms timeline link if venue has no dms application', () => {
    props.venue.collectiveDmsApplications = []

    renderVenue(props)

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display API tag if venue has at least one provider', async () => {
    props.venue.hasVenueProviders = true
    renderVenue(props)

    await screen.findByText('API')
  })
})
