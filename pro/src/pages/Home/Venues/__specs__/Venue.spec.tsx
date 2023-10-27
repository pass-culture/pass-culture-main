import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import { api } from 'apiClient/api'
import { DMSApplicationstatus } from 'apiClient/v1'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Venue, { VenueProps } from '../Venue'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueStats: vi.fn(),
  },
}))

const renderVenue = (
  props: VenueProps,
  features?: { list: { isActive: true; nameKey: string }[] }
) => {
  const storeOverrides = {
    features: features,
  }
  renderWithProviders(<Venue {...props} />, {
    storeOverrides: { ...storeOverrides },
  })
}

describe('venues', () => {
  let props: VenueProps
  const offererId = 12
  const venueId = 1

  beforeEach(() => {
    props = {
      venueId: venueId,
      isVirtual: false,
      name: 'My venue',
      offererId: offererId,
      dmsInformations: null,
    }
    vi.spyOn(api, 'getVenueStats').mockResolvedValue({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
  })

  it('should display stats tiles', async () => {
    renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getVenueStats).toHaveBeenCalledWith(props.venueId)

    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')

    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    expect(
      within(activeOffersStat).getByText('Offres publiées')
    ).toBeInTheDocument()

    expect(within(activeBookingsStat).getByText('0')).toBeInTheDocument()
    expect(
      within(activeBookingsStat).getByText('Réservations en cours')
    ).toBeInTheDocument()

    expect(within(validatedBookingsStat).getByText('1')).toBeInTheDocument()
    expect(
      within(validatedBookingsStat).getByText('Réservations validées')
    ).toBeInTheDocument()

    expect(within(outOfStockOffersStat).getByText('3')).toBeInTheDocument()
    expect(
      within(outOfStockOffersStat).getByText('Offres stocks épuisés')
    ).toBeInTheDocument()
  })

  it('should contain a link for each stats', async () => {
    renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const [activeOffersStat] = screen.getAllByTestId('venue-stat')
    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    expect(screen.getAllByRole('link', { name: /Voir/ })).toHaveLength(4)
  })

  describe('physical venue section', () => {
    it('should display edition venue link', async () => {
      props.isVirtual = false

      renderVenue(props)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.getByRole('link', { name: 'Éditer le lieu' })
      ).toHaveAttribute(
        'href',
        `/structures/${offererId}/lieux/${venueId}?modification`
      )
    })

    it('should display add bank information when venue does not have a reimbursement point', () => {
      props.hasMissingReimbursementPoint = true
      props.hasCreatedOffer = true

      renderVenue(props)

      expect(
        screen.getByRole('link', { name: 'Ajouter un RIB' })
      ).toHaveAttribute(
        'href',
        `/structures/${offererId}/lieux/${venueId}?modification#remboursement`
      )
    })

    it('should not display add bank information when for the new bank details journey is enabled', () => {
      props.hasMissingReimbursementPoint = true
      props.hasCreatedOffer = true

      renderVenue(props, {
        list: [
          { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
        ],
      })

      expect(
        screen.queryByRole('link', { name: 'Ajouter un RIB' })
      ).not.toBeInTheDocument()
    })
  })

  it('should not display dms timeline link if venue has no dms application', async () => {
    renderVenue({
      ...props,
      hasAdageId: false,
      dmsInformations: null,
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display dms timeline link when venue has dms applicaiton and adage id less than 30 days', async () => {
    renderVenue({
      ...props,
      hasAdageId: true,
      adageInscriptionDate: addDays(new Date(), -15).toISOString(),
      dmsInformations: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toHaveAttribute(
      'href',
      `/structures/${offererId}/lieux/${venueId}#venue-collective-data`
    )
  })
  it('should not display dms timeline link if venue has adageId for more than 30days', async () => {
    renderVenue({
      ...props,
      hasAdageId: true,
      adageInscriptionDate: addDays(new Date(), -32).toISOString(),
      dmsInformations: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display dms timeline link if venue has refused application for less than 30days', async () => {
    renderVenue({
      ...props,
      dmsInformations: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.REFUSE,
        processingDate: addDays(new Date(), -15).toISOString(),
      },
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.getByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).toBeInTheDocument()
  })

  it('should not display dms timeline link if venue has refused application for more than 30days', async () => {
    renderVenue({
      ...props,
      dmsInformations: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.REFUSE,
        processingDate: addDays(new Date(), -31).toISOString(),
      },
    })
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByRole('link', {
        name: 'Suivre ma demande de référencement ADAGE',
      })
    ).not.toBeInTheDocument()
  })

  it('should display API tag if venue has at least one provider', async () => {
    props.hasProvider = true
    renderVenue(props)
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    await screen.findByText('API')
  })
})
