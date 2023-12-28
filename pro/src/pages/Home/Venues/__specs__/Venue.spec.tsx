import { screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

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
      ).toHaveAttribute(
        'href',
        `/structures/${offererId}/lieux/${venueId}?modification`
      )
    })

    it('should display add bank information when venue does not have a reimbursement point', () => {
      props.venue.hasMissingReimbursementPoint = true
      props.venue.hasCreatedOffer = true

      renderVenue(props)

      expect(
        screen.getByRole('link', { name: 'Ajouter un RIB' })
      ).toHaveAttribute(
        'href',
        `/structures/${offererId}/lieux/${venueId}?modification#remboursement`
      )
    })

    it('should not display add bank information when for the new bank details journey is enabled', () => {
      props.venue.hasMissingReimbursementPoint = true
      props.venue.hasCreatedOffer = true

      renderVenue(props, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.queryByRole('link', { name: 'Ajouter un RIB' })
      ).not.toBeInTheDocument()
    })
  })

  it('should not display dms timeline link if venue has no dms application', () => {
    props.venue.hasAdageId = false
    props.venue.collectiveDmsApplications = []

    renderVenue(props)

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display dms timeline link when venue has dms applicaiton and adage id less than 30 days', () => {
    props.venue.hasAdageId = true
    props.venue.adageInscriptionDate = addDays(new Date(), -15).toISOString()
    props.venue.collectiveDmsApplications = [
      {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
    ]

    renderVenue(props)

    expect(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toHaveAttribute(
      'href',
      `/structures/${offererId}/lieux/${venueId}#venue-collective-data`
    )
  })

  it('should not display dms timeline link if venue has adageId for more than 30days', () => {
    props.venue.hasAdageId = true
    props.venue.adageInscriptionDate = addDays(new Date(), -32).toISOString()
    props.venue.collectiveDmsApplications = [
      {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
    ]

    renderVenue(props)

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display dms timeline link if venue has refused application for less than 30days', () => {
    props.venue.collectiveDmsApplications = [
      {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.REFUSE,
        processingDate: addDays(new Date(), -15).toISOString(),
      },
    ]

    renderVenue(props)

    expect(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toBeInTheDocument()
  })

  it('should not display dms timeline link if venue has refused application for more than 30days', () => {
    props.venue.collectiveDmsApplications = [
      {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.REFUSE,
        processingDate: addDays(new Date(), -31).toISOString(),
      },
    ]

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
