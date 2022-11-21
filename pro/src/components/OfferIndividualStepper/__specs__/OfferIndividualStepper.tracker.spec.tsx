import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter, Route, Switch } from 'react-router'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import * as useAnalytics from 'hooks/useAnalytics'

import OfferIndividualStepper from '../OfferIndividualStepper'

const mockLogEvent = jest.fn()

const renderOfferIndividualStepper = (
  contextOverride: Partial<IOfferIndividualContext> = {},
  url = '/offre/AA/v3/creation/individuelle/informations'
) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    ...contextOverride,
  }
  const rtlReturns = render(
    <OfferIndividualContext.Provider value={contextValues}>
      <MemoryRouter initialEntries={[url]}>
        <OfferIndividualStepper />
        <Switch>
          <Route
            path={[
              '/offre/:offerId/v3/brouillon/individuelle/informations',
              '/offre/:offerId/v3/creation/individuelle/informations',
              '/offre/:offerId/v3/individuelle/informations',
            ]}
          >
            <div>Informations screen</div>
          </Route>
          <Route
            path={[
              '/offre/:offerId/v3/brouillon/individuelle/stocks',
              '/offre/:offerId/v3/creation/individuelle/stocks',
              '/offre/:offerId/v3/individuelle/stocks',
            ]}
          >
            <div>Stocks screen</div>
          </Route>
          <Route
            path={[
              '/offre/:offerId/v3/brouillon/individuelle/recapitulatif',
              '/offre/:offerId/v3/creation/individuelle/recapitulatif',
              '/offre/:offerId/v3/individuelle/recapitulatif',
            ]}
          >
            <div>Summary screen</div>
          </Route>
          <Route
            path={['/offre/:offerId/v3/creation/individuelle/confirmation']}
          >
            <div>Confirmation screen</div>
          </Route>
        </Switch>
      </MemoryRouter>
    </OfferIndividualContext.Provider>
  )

  const tabInformations = screen.queryByText('Détails de l’offre')
  const tabStocks = screen.queryByText('Stock & Prix')
  const tabSummary = screen.queryByText('Récapitulatif')

  return {
    ...rtlReturns,
    tabInformations,
    tabStocks,
    tabSummary,
  }
}

describe('test tracker OfferIndividualStepper', () => {
  let offer: Partial<IOfferIndividual>
  let contextOverride: Partial<IOfferIndividualContext>
  beforeEach(() => {
    offer = {
      id: 'AA',
      stocks: [{ id: 'STOCK_ID' } as IOfferIndividualStock],
    }

    contextOverride = {
      offer: offer as IOfferIndividual,
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  describe('in creation', () => {
    it('should track when clicking on steps on Information', async () => {
      const { tabStocks } = renderOfferIndividualStepper(contextOverride)

      tabStocks && (await userEvent.click(tabStocks))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: false,
          isDraft: true,
          offerId: 'AA',
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      const { tabSummary } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/creation/individuelle/stocks'
      )

      tabSummary && (await userEvent.click(tabSummary))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: false,
          isDraft: true,
          offerId: 'AA',
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Summary', async () => {
      const { tabInformations } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/creation/individuelle/recapitulatif'
      )

      tabInformations && (await userEvent.click(tabInformations))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          isDraft: true,
          offerId: 'AA',
          to: 'informations',
          used: 'Breadcrumb',
        }
      )
    })
  })

  describe('in edition', () => {
    it('should track when clicking on steps on Information', async () => {
      const { tabStocks } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/individuelle/informations'
      )

      tabStocks && (await userEvent.click(tabStocks))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: true,
          isDraft: false,
          offerId: 'AA',
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      const { tabInformations } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/individuelle/stocks'
      )

      tabInformations && (await userEvent.click(tabInformations))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: true,
          isDraft: false,
          offerId: 'AA',
          to: 'informations',
          used: 'Breadcrumb',
        }
      )
    })
  })

  describe('in draft', () => {
    it('should track when clicking on steps on Information', async () => {
      const { tabSummary } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/brouillon/individuelle/informations'
      )

      tabSummary && (await userEvent.click(tabSummary))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: true,
          isDraft: true,
          offerId: 'AA',
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      const { tabSummary } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/brouillon/individuelle/stocks'
      )

      tabSummary && (await userEvent.click(tabSummary))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: true,
          isDraft: true,
          offerId: 'AA',
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Summary', async () => {
      const { tabStocks } = renderOfferIndividualStepper(
        contextOverride,
        '/offre/AA/v3/brouillon/individuelle/recapitulatif'
      )

      tabStocks && (await userEvent.click(tabStocks))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          isDraft: true,
          offerId: 'AA',
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })
  })
})
