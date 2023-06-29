import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import {
  OfferIndividualContextValues,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OfferIndividual, OfferIndividualVenue } from 'core/Offers/types'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import Stocks from '../Stocks'

const renderStocksScreen = (
  storeOverrides: Partial<RootState> = {},
  contextOverride: Partial<OfferIndividualContextValues>
) => {
  const contextValue: OfferIndividualContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    shouldTrack: true,
    setShouldTrack: () => {},
    showVenuePopin: {},
    ...contextOverride,
  }
  return renderWithProviders(
    <OfferIndividualContext.Provider value={contextValue}>
      <Stocks />
    </OfferIndividualContext.Provider>,
    { storeOverrides }
  )
}

describe('screens:Stocks', () => {
  let storeOverrides: Partial<RootState>
  let contextOverride: Partial<OfferIndividualContextValues>
  let offer: Partial<OfferIndividual>
  const offerId = 12

  beforeEach(() => {
    offer = {
      id: offerId,
      venue: {
        departmentCode: '75',
      } as OfferIndividualVenue,
      stocks: [],
    }
    storeOverrides = {}
    contextOverride = {
      offerId: offerId,
      offer: offer as OfferIndividual,
    }
  })

  it('should render stock thing', async () => {
    contextOverride.offer = {
      ...contextOverride.offer,
      isEvent: false,
      isDigital: false,
    } as OfferIndividual
    renderStocksScreen(storeOverrides, contextOverride)

    expect(
      screen.getByText(
        'Les bénéficiaires ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
  })

  it('should render stock event', async () => {
    contextOverride.offer = {
      ...contextOverride.offer,
      isEvent: true,
    } as OfferIndividual
    renderStocksScreen(storeOverrides, contextOverride)

    await waitFor(() => {
      expect(
        screen.getByText(
          'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
        )
      ).toBeInTheDocument()
    })
  })

  const offerStatusWithoutBanner = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(offerStatusWithoutBanner)(
    'should not render stock description banner',
    async offerStatus => {
      contextOverride.offer = {
        ...contextOverride.offer,
        isEvent: true,
        status: offerStatus,
      } as OfferIndividual
      renderStocksScreen(storeOverrides, contextOverride)

      await waitFor(() => {
        expect(
          screen.queryByText(
            'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
          )
        ).not.toBeInTheDocument()
      })
    }
  )

  const offerStatusWithBanner = [
    OfferStatus.ACTIVE,
    OfferStatus.EXPIRED,
    OfferStatus.SOLD_OUT,
    OfferStatus.INACTIVE,
    OfferStatus.DRAFT,
  ]
  it.each(offerStatusWithBanner)(
    'should render stock description banner',
    async offerStatus => {
      contextOverride.offer = {
        ...contextOverride.offer,
        isEvent: true,
        status: offerStatus,
      } as OfferIndividual
      renderStocksScreen(storeOverrides, contextOverride)

      await waitFor(() => {
        expect(
          screen.queryByText(
            'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
          )
        ).toBeInTheDocument()
      })
    }
  )
})
