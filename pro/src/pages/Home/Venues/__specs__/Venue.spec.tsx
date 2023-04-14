import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import React from 'react'

import { api } from 'apiClient/api'
import { DMSApplicationstatus } from 'apiClient/v1'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { loadFakeApiVenueStats } from 'utils/fakeApi'
import { renderWithProviders } from 'utils/renderWithProviders'

import Venue, { IVenueProps } from '../Venue'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueStats: jest.fn().mockResolvedValue({}),
  },
}))

const renderVenue = (
  props: IVenueProps,
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
  let props: IVenueProps

  beforeEach(() => {
    props = {
      id: 'VENUE01',
      nonHumanizedId: 1,
      isVirtual: false,
      name: 'My venue',
      offererId: 'OFFERER01',
      dmsInformations: null,
    }
    loadFakeApiVenueStats({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
  })

  it('should display stats tiles', async () => {
    // When
    renderVenue(props)

    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )

    // Then
    expect(api.getVenueStats).toHaveBeenCalledWith(props.nonHumanizedId)

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
    // When
    renderVenue(props)
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
    const [activeOffersStat] = screen.getAllByTestId('venue-stat')
    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    // Then
    expect(screen.getAllByRole('link', { name: 'Voir' })).toHaveLength(4)
  })

  it('should redirect to filtered bookings when clicking on link', async () => {
    // When
    renderVenue(props)
    await userEvent.click(
      screen.getByTitle('Afficher les statistiques de My venue')
    )
    // Then
    const [
      activeOffersStat,
      activeBookingsStat,
      validatedBookingsStat,
      outOfStockOffersStat,
    ] = screen.getAllByTestId('venue-stat')

    expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

    expect(
      within(activeOffersStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/offres?lieu=VENUE01&statut=active')
    const byRole = within(validatedBookingsStat).getByRole('link', {
      name: 'Voir',
    })
    expect(byRole).toHaveAttribute(
      'href',
      '/reservations?page=1&bookingStatusFilter=validated&offerVenueId=VENUE01'
    )
    expect(
      within(activeBookingsStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/reservations?page=1&offerVenueId=VENUE01')
    expect(
      within(outOfStockOffersStat).getByRole('link', { name: 'Voir' })
    ).toHaveAttribute('href', '/offres?lieu=VENUE01&statut=epuisee')
  })

  describe('virtual venue section', () => {
    it('should display create offer link', async () => {
      // Given
      props.isVirtual = true

      // When
      renderVenue(props)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

      // Then
      expect(
        screen.getByRole('link', { name: 'Créer une nouvelle offre numérique' })
      ).toBeInTheDocument()
    })
  })

  describe('physical venue section', () => {
    it('should display create offer link', async () => {
      // Given
      props.isVirtual = false

      // When
      renderVenue(props)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

      // Then
      expect(
        screen.getByRole('link', { name: 'Créer une nouvelle offre' })
      ).toBeInTheDocument()
    })

    it('should display edition venue link', async () => {
      // Given
      props.isVirtual = false

      // When
      renderVenue(props)
      await userEvent.click(
        screen.getByTitle('Afficher les statistiques de My venue')
      )
      const [activeOffersStat] = screen.getAllByTestId('venue-stat')
      expect(within(activeOffersStat).getByText('2')).toBeInTheDocument()

      // Then
      expect(screen.getByRole('link', { name: 'Modifier' })).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification'
      )
    })

    it('should display edition venue link with new offer creation journey', async () => {
      // Given
      props.isVirtual = false
      await jest
        .spyOn(useNewOfferCreationJourney, 'default')
        .mockReturnValue(true)
      // When
      renderVenue(props)

      // Then
      expect(
        screen.getByRole('link', { name: 'Éditer le lieu' })
      ).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification'
      )
    })

    it('should display add bank information when venue does not have a reimbursement point', () => {
      // Given
      props.hasMissingReimbursementPoint = true
      props.hasCreatedOffer = true

      // When
      renderVenue(props)

      // Then
      expect(
        screen.getByRole('link', { name: 'Ajouter un RIB' })
      ).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01?modification#remboursement'
      )
    })
    it('should display dms timeline link when venue has dms applicaiton and adage id less than 30 days', async () => {
      // When
      await jest
        .spyOn(useNewOfferCreationJourney, 'default')
        .mockReturnValue(false)
      renderVenue(
        {
          ...props,
          initialOpenState: true,
          hasAdageId: true,
          adageInscriptionDate: addDays(new Date(), -15).toISOString(),
          dmsInformations: {
            ...defaultCollectiveDmsApplication,
            state: DMSApplicationstatus.ACCEPTE,
          },
        },
        {
          list: [
            {
              isActive: true,
              nameKey: 'WIP_ENABLE_COLLECTIVE_DMS_TRACKING',
            },
          ],
        }
      )
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      // Then
      expect(
        screen.getByRole('link', {
          name: 'Suivre ma demande de référencement ADAGE',
        })
      ).toHaveAttribute(
        'href',
        '/structures/OFFERER01/lieux/VENUE01#reimbursement'
      )
    })
  })
})
