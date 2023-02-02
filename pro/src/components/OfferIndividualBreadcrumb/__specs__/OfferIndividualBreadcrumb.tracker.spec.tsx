import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath } from 'react-router'
import { Route, Routes } from 'react-router-dom-v5-compat'

import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import OfferIndividualBreadcrumb from '../OfferIndividualBreadcrumb'

const mockLogEvent = jest.fn()

const renderOfferIndividualBreadcrumb = (
  contextOverride: Partial<IOfferIndividualContext> = {},
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  })
) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  const rtlReturns = renderWithProviders(
    <OfferIndividualContext.Provider value={contextValues}>
      <OfferIndividualBreadcrumb />
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode,
            })}
            element={<div>Informations screen</div>}
          />
        ))}

        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode,
            })}
            element={<div>Stocks screen</div>}
          />
        ))}

        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode,
            })}
            element={<div>Summary screen</div>}
          />
        ))}

        <Route
          path={getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </OfferIndividualContext.Provider>,
    { initialRouterEntries: [url] }
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

describe('test tracker OfferIndividualBreadcrumb', () => {
  let offer: Partial<IOfferIndividual>
  let contextOverride: Partial<IOfferIndividualContext>
  beforeEach(() => {
    offer = individualOfferFactory({ id: 'AA' })

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
      const { tabStocks } = renderOfferIndividualBreadcrumb(contextOverride)

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
      const { tabSummary } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
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
      const { tabInformations } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
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
      const { tabStocks } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        )
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
      const { tabInformations } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        )
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
      const { tabSummary } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: 'AA' }
        )
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
      const { tabSummary } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: 'AA' }
        )
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
      const { tabStocks } = renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: 'AA' }
        )
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
