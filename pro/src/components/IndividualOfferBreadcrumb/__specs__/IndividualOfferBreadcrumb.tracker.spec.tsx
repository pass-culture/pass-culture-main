import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OFFER_WIZARD_STEP_IDS } from '../constants'
import { IndividualOfferBreadcrumb } from '../IndividualOfferBreadcrumb'

const mockLogEvent = vi.fn()

const renderIndividualOfferBreadcrumb = (
  contextOverride: Partial<IndividualOfferContextValues> = {},
  url = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    mode: OFFER_WIZARD_MODE.CREATION,
  })
) => {
  const contextValues: IndividualOfferContextValues = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    setSubcategory: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...contextOverride,
  }

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferBreadcrumb />
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode,
            })}
            element={<div>Informations screen</div>}
          />
        ))}

        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.STOCKS,
              mode,
            })}
            element={<div>Stocks screen</div>}
          />
        ))}

        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode,
            })}
            element={<div>Summary screen</div>}
          />
        ))}

        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Confirmation screen</div>}
        />
      </Routes>
    </IndividualOfferContext.Provider>,
    { initialRouterEntries: [url] }
  )
}

describe('test tracker IndividualOfferBreadcrumb', () => {
  let offer: Partial<IndividualOffer>
  let contextOverride: Partial<IndividualOfferContextValues>
  const offerId = 1
  beforeEach(() => {
    offer = individualOfferFactory({ id: offerId })
    contextOverride = {
      offer: offer as IndividualOffer,
    }
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })
  describe('in creation', () => {
    it('should track when clicking on steps on Information', async () => {
      renderIndividualOfferBreadcrumb(contextOverride)

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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
      renderIndividualOfferBreadcrumb(
        contextOverride,
        generatePath(
          getIndividualOfferPath({
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
