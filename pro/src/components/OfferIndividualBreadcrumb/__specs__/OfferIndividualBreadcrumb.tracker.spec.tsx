import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import {
  OfferIndividualContextValues,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { OfferIndividual } from 'core/Offers/types'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import OfferIndividualBreadcrumb from '../OfferIndividualBreadcrumb'

const mockLogEvent = jest.fn()

const renderOfferIndividualBreadcrumb = (
  contextOverride: Partial<OfferIndividualContextValues> = {},
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  })
) => {
  const contextValues: OfferIndividualContextValues = {
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

  renderWithProviders(
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
}

describe('test tracker OfferIndividualBreadcrumb', () => {
  let offer: Partial<OfferIndividual>
  let contextOverride: Partial<OfferIndividualContextValues>
  const offerId = 1
  beforeEach(() => {
    offer = individualOfferFactory({ id: offerId })
    contextOverride = {
      offer: offer as OfferIndividual,
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  describe('in creation', () => {
    it('should track when clicking on steps on Information', async () => {
      renderOfferIndividualBreadcrumb(contextOverride)

      await userEvent.click(screen.getByText('Dates & Capacités'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: false,
          isDraft: true,
          offerId: offerId,
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: false,
          isDraft: true,
          offerId: offerId,
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Summary', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Détails de l’offre'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: false,
          isDraft: true,
          offerId: offerId,
          to: 'informations',
          used: 'Breadcrumb',
        }
      )
    })
  })

  describe('in edition', () => {
    it('should track when clicking on steps on Information', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Dates & Capacités'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: true,
          isDraft: false,
          offerId: offerId,
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Détails de l’offre'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: true,
          isDraft: false,
          offerId: offerId,
          to: 'informations',
          used: 'Breadcrumb',
        }
      )
    })
  })

  describe('in draft', () => {
    it('should track when clicking on steps on Information', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'informations',
          isEdition: true,
          isDraft: true,
          offerId: offerId,
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Stocks', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'stocks',
          isEdition: true,
          isDraft: true,
          offerId: offerId,
          to: 'recapitulatif',
          used: 'Breadcrumb',
        }
      )
    })

    it('should track when clicking on steps on Summary', async () => {
      renderOfferIndividualBreadcrumb(
        contextOverride,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.DRAFT,
          }),
          { offerId: offerId }
        )
      )

      await userEvent.click(screen.getByText('Dates & Capacités'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'recapitulatif',
          isEdition: true,
          isDraft: true,
          offerId: offerId,
          to: 'stocks',
          used: 'Breadcrumb',
        }
      )
    })
  })
})
