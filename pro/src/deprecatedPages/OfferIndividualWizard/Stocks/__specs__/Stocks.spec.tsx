import { screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { IOfferIndividual, IOfferIndividualVenue } from 'core/Offers/types'
import { RootState } from 'store/reducers'
import { renderWithProviders } from 'utils/renderWithProviders'

import Stocks from '../Stocks'

const renderStocksScreen = (
  storeOverrides: Partial<RootState> = {},
  contextOverride: Partial<IOfferIndividualContext>
) => {
  const contextValue: IOfferIndividualContext = {
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
    { storeOverrides, initialRouterEntries: ['/creation/stocks'] }
  )
}

describe('screens:Stocks', () => {
  let storeOverrides: Partial<RootState>
  let contextOverride: Partial<IOfferIndividualContext>
  let offer: Partial<IOfferIndividual>

  beforeEach(() => {
    offer = {
      id: 'OFFER_ID',
      venue: {
        departmentCode: '75',
      } as IOfferIndividualVenue,
      stocks: [],
    }
    storeOverrides = {}
    contextOverride = {
      offerId: 'OFFER_ID',
      offer: offer as IOfferIndividual,
    }
  })

  it('should render stock thing', async () => {
    contextOverride.offer = {
      ...contextOverride.offer,
      isEvent: false,
      isDigital: false,
    } as IOfferIndividual
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
    } as IOfferIndividual
    renderStocksScreen(storeOverrides, contextOverride)
    expect(
      screen.getByText(
        'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
      )
    ).toBeInTheDocument()
  })

  const offerStatusWithoutBanner = [OfferStatus.REJECTED, OfferStatus.PENDING]
  it.each(offerStatusWithoutBanner)(
    'should not render stock description banner',
    async offerStatus => {
      contextOverride.offer = {
        ...contextOverride.offer,
        isEvent: true,
        status: offerStatus,
      } as IOfferIndividual
      renderStocksScreen(storeOverrides, contextOverride)
      expect(
        screen.queryByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
        )
      ).not.toBeInTheDocument()
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
      } as IOfferIndividual
      renderStocksScreen(storeOverrides, contextOverride)
      expect(
        screen.queryByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
        )
      ).toBeInTheDocument()
    }
  )
})
