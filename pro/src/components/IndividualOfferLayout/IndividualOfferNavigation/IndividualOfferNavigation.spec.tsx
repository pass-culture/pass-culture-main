import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  priceCategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  RenderComponentFunction,
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { IndividualOfferNavigation } from './IndividualOfferNavigation'
import { getLocalStorageKeyName } from './utils/handleLastSubmittedStep'

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

  renderWithProviders(
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

  it('should always display "Détails" and "Informations pratiques" steps', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: offerBase,
    })

    renderIndividualOfferNavigation({ contextValues })

    const steps = screen.getAllByRole('listitem')

    const detailsStep = steps.find((listitem) =>
      listitem.textContent?.match(LABELS.DETAILS)
    )
    expect(detailsStep).toBeDefined()

    const usefulInformationsStep = steps.find((listitem) =>
      listitem.textContent?.match(LABELS.USEFUL_INFORMATIONS)
    )
    expect(usefulInformationsStep).toBeDefined()
  })

  it('should display "Image et vidéo" step when WIP_ADD_VIDEO is enabled', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: offerBase,
    })
    const options: RenderWithProvidersOptions = {
      features: ['WIP_ADD_VIDEO'],
    }

    renderIndividualOfferNavigation({ contextValues, options })

    const mediaStep = screen
      .getAllByRole('listitem')
      .find((listitem) => listitem.textContent?.match(LABELS.MEDIA))
    expect(mediaStep).toBeDefined()
  })

  describe('when offer is an event', () => {
    const contextValues = individualOfferContextValuesFactory({
      isEvent: true,
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: offerBase,
    })

    it('should display "Tarifs" and "Dates & Capacités" steps', () => {
      renderIndividualOfferNavigation({
        contextValues,
      })

      const steps = screen.getAllByRole('listitem')

      const pricesStep = steps.find((listitem) =>
        listitem.textContent?.match(LABELS.PRICES)
      )
      expect(pricesStep).toBeDefined()

      const datesCapacities = steps.find((listitem) =>
        listitem.textContent?.match(LABELS.DATES_CAPACITIES)
      )
      expect(datesCapacities).toBeDefined()
    })

    it('should never display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({ contextValues })

      const stockPricesStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.STOCK_PRICES))
      expect(stockPricesStep).not.toBeDefined()
    })
  })

  describe('when offer is not an event', () => {
    const contextValues = individualOfferContextValuesFactory({
      isEvent: null,
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: offerBase,
    })

    it('should display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({
        contextValues,
      })

      const stockStep = screen
        .getAllByRole('listitem')
        .find((listitem) => listitem.textContent?.match(LABELS.STOCK_PRICES))
      expect(stockStep).toBeDefined()
    })
  })

  describe('on creation mode', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: offerBase,
    })
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    it('should only display some steps as links when those where submitted', () => {
      localStorage.setItem(
        getLocalStorageKeyName(offerBase.id),
        INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
      )

      renderIndividualOfferNavigation({ contextValues, path })

      const steps = screen.getAllByRole('listitem')
      const submittedStepIndex = steps.findIndex((listItem) =>
        listItem.textContent?.match(LABELS.USEFUL_INFORMATIONS)
      )

      const links = screen.getAllByRole('link')
      expect(links.length).toEqual(submittedStepIndex + 1)

      localStorage.clear()
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
  })

  describe('on edition mode', () => {
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

  describe('with WIP_ENABLE_NEW_OFFER_CREATION_FLOW feature flag', () => {
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

    const options: RenderWithProvidersOptions = {
      features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'],
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

      renderIndividualOfferNavigation({ contextValues, options })

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

      renderIndividualOfferNavigation({ contextValues, options })

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
  })
})
