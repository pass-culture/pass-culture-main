import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  priceCategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { IndividualOfferNavigation } from './IndividualOfferNavigation'

const renderIndividualOfferNavigation: RenderComponentFunction<
  void,
  IndividualOfferContextValues
> = (params) => {
  const contextValues = {
    ...individualOfferContextValuesFactory({
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: null,
    }),
    ...params.contextValues,
  }

  const path =
    params.path ??
    getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.CREATION,
    })
  const overrides: RenderWithProvidersOptions = {
    initialRouterEntries: [path],
    ...params.options,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferNavigation />
    </IndividualOfferContext.Provider>,
    overrides
  )
}

const LABELS = {
  DETAILS: /Détails/,
  USEFUL_INFORMATIONS: /Informations pratiques/,
  MEDIA: /Image et vidéo/,
  PRICES: /Tarifs/,
  DATES_CAPACITIES: /Dates/,
  STOCK_PRICES: /Stock/,
  SUMMARY: /Récapitulatif/,
  BOOKING: /Réservation/,
}

describe('IndividualOfferNavigation', () => {
  const offerBase = getIndividualOfferFactory({
    isEvent: false,
    hasStocks: false,
    priceCategories: [],
  })

  describe('when offer is an event', () => {
    const contextValues = individualOfferContextValuesFactory({
      isEvent: true,
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: {
        ...offerBase,
        isEvent: true,
      },
    })

    it('should never display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({ contextValues })

      const stockPricesStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.STOCK_PRICES))
      expect(stockPricesStep).not.toBeDefined()
    })
  })

  describe('on creation mode', () => {
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    it('should display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      const summaryStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.SUMMARY))
      expect(summaryStep).toBeDefined()
    })

    it('should never display "Réservation" step', () => {
      renderIndividualOfferNavigation({})

      const bookingStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.BOOKING))
      expect(bookingStep).not.toBeDefined()
    })

    it('should only display some steps as links when those where submitted', () => {
      const offerWithNumerousStepsBase = getIndividualOfferFactory({
        isEvent: true,
        priceCategories: [priceCategoryFactory()],
        location: getLocationResponseModel(),
        hasStocks: false,
      })
      const contextValuesWithNumerousSteps =
        individualOfferContextValuesFactory({
          isEvent: true,
          offer: offerWithNumerousStepsBase,
        })

      renderIndividualOfferNavigation({
        contextValues: contextValuesWithNumerousSteps,
        path,
      })

      const steps = screen.getAllByRole('listitem')
      const lastSubmittedStepIndex = steps.findIndex((listItem) =>
        listItem.textContent?.match(LABELS.PRICES)
      )

      const links = screen.getAllByRole('link')
      // +1 since steps is an array starting at 0.
      // +1 since we'd like to access the step following the submitted one.
      expect(links.length).toEqual(lastSubmittedStepIndex + 2)
    })
  })

  describe('on edition mode', () => {
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    it('should display all steps as links', () => {
      renderIndividualOfferNavigation({ path })

      const steps = screen.getAllByRole('listitem')
      const links = screen.getAllByRole('link')
      expect(steps.length).toEqual(links.length)
    })

    it('should display "Réservation" step', () => {
      renderIndividualOfferNavigation({ path })

      const bookingStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.BOOKING))
      expect(bookingStep).not.toBeDefined()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      const summaryStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.SUMMARY))
      expect(summaryStep).not.toBeDefined()
    })
  })

  describe('on read-only mode', () => {
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    it('should display all steps as links', () => {
      renderIndividualOfferNavigation({ path })

      const steps = screen.getAllByRole('listitem')
      const links = screen.getAllByRole('link')
      expect(steps.length).toEqual(links.length)
    })

    it('should display "Réservation" step', () => {
      renderIndividualOfferNavigation({ path })

      const bookingStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.BOOKING))
      expect(bookingStep).toBeDefined()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      const summaryStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.SUMMARY))
      expect(summaryStep).not.toBeDefined()
    })
  })

  describe('offer creation stepper', () => {
    // Will be merged once the feature is enabled in production.
    const FF_LABELS = {
      links: {
        DESCRIPTION: /Description/,
        LOCALISATION: /Localisation/,
        PRICE_LIST: /Tarifs/,
        TIMETABLE: /Horaires/,
        SUMMARY: /Récapitulatif/,
      },
    }

    it.each([
      {
        description: "we don't know yet is the offer is an event or not",
        isEvent: null,
      },
      { description: 'the offer is an event', isEvent: true },
    ])('should display the expected steps when $description', ({ isEvent }) => {
      const contextValues = individualOfferContextValuesFactory({
        isEvent,
      })

      renderIndividualOfferNavigation({ contextValues })

      const steps = screen.getAllByRole('listitem')
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.DESCRIPTION)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.LOCALISATION)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.PRICE_LIST)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.TIMETABLE)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.SUMMARY)
        )
      ).toBeDefined()
    })

    it('should display the expected steps when the offer is NOT an event', () => {
      const contextValues = individualOfferContextValuesFactory({
        isEvent: false,
      })

      renderIndividualOfferNavigation({ contextValues })

      const steps = screen.getAllByRole('listitem')
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.DESCRIPTION)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.LOCALISATION)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.PRICE_LIST)
        )
      ).toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.TIMETABLE)
        )
      ).not.toBeDefined()
      expect(
        steps.find((listitem) =>
          listitem.textContent?.match(FF_LABELS.links.SUMMARY)
        )
      ).toBeDefined()
    })

    it('should display the expected active steps when the offer is completed', () => {
      const contextValues = individualOfferContextValuesFactory({
        isEvent: true,
        offer: getIndividualOfferFactory({
          audioDisabilityCompliant: true,
          location: getLocationResponseModel(),
        }),
      })

      renderIndividualOfferNavigation({ contextValues })

      const locationStep = screen.getByRole('link', { name: '7 Récapitulatif' })

      expect(locationStep).toBeInTheDocument()
    })
  })
})
