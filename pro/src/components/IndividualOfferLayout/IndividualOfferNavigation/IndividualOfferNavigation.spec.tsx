import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  priceCategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  RenderComponentFunction,
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import {
  IndividualOfferNavigation,
  IndividualOfferNavigationProps,
} from './IndividualOfferNavigation'

const renderIndividualOfferNavigation: RenderComponentFunction<
  IndividualOfferNavigationProps,
  IndividualOfferContextValues
> = (params) => {
  const contextValues = {
    ...individualOfferContextValuesFactory({
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: null,
    }),
    ...params.contextValues,
  }
  const props: IndividualOfferNavigationProps = {
    isUsefulInformationSubmitted: false,
    ...params.props,
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
      <IndividualOfferNavigation {...props} />
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

  it('should always display "Détails" and "Informations pratiques" active/enabled steps', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: offerBase,
    })

    renderIndividualOfferNavigation({ contextValues })

    const detailsStep = screen.getByRole('link', { name: LABELS.DETAILS })
    expect(detailsStep).toBeInTheDocument()

    const usefulInformationsStep = screen.getByRole('link', {
      name: LABELS.USEFUL_INFORMATIONS,
    })
    expect(usefulInformationsStep).toBeInTheDocument()
  })

  it('should display "Image et vidéo" active step when WIP_ADD_VIDEO is enabled', () => {
    const contextValues = individualOfferContextValuesFactory({
      offer: offerBase,
    })
    const options: RenderWithProvidersOptions = {
      features: ['WIP_ADD_VIDEO'],
    }

    renderIndividualOfferNavigation({ contextValues, options })

    const mediaStep = screen.getByRole('link', { name: LABELS.MEDIA })
    expect(mediaStep).toBeInTheDocument()
  })

  describe('when offer is an event', () => {
    const contextValuesBase = individualOfferContextValuesFactory({
      isEvent: true,
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: offerBase,
    })

    it('should display "Tarifs" and "Dates & Capacités" steps', () => {
      const props: IndividualOfferNavigationProps = {
        isUsefulInformationSubmitted: false,
      }

      renderIndividualOfferNavigation({
        contextValues: contextValuesBase,
        props,
      })

      const pricesStepAsALink = screen.queryByRole('link', {
        name: LABELS.PRICES,
      })
      expect(pricesStepAsALink).not.toBeInTheDocument()
      const pricesStep = screen.getByText(LABELS.PRICES)
      expect(pricesStep).toBeInTheDocument()

      const datesCapacitiesStepAsALink = screen.queryByRole('link', {
        name: LABELS.DATES_CAPACITIES,
      })
      expect(datesCapacitiesStepAsALink).not.toBeInTheDocument()
      const datesCapacitiesStep = screen.getByText(LABELS.DATES_CAPACITIES)
      expect(datesCapacitiesStep).toBeInTheDocument()
    })

    it('should display "Tarifs" step as active/enabled when offer is no longer a non-published draft', () => {
      const props: IndividualOfferNavigationProps = {
        isUsefulInformationSubmitted: true,
      }

      renderIndividualOfferNavigation({
        contextValues: contextValuesBase,
        props,
      })

      const pricesStep = screen.getByText(LABELS.PRICES)
      expect(pricesStep).toBeInTheDocument()

      const datesCapacitiesStep = screen.getByText(LABELS.DATES_CAPACITIES)
      expect(datesCapacitiesStep).toBeInTheDocument()
    })

    it('should display "Tarifs" step as active/enabled when offer has price categories', () => {
      const contextValues: IndividualOfferContextValues = {
        ...contextValuesBase,
        isEvent: true,
        offer: {
          ...offerBase,
          priceCategories: [priceCategoryFactory()],
        },
      }

      renderIndividualOfferNavigation({ contextValues })

      const pricesStep = screen.getByText(LABELS.PRICES)
      expect(pricesStep).toBeInTheDocument()
    })

    it('should display "Dates et Capacités" step as active/enabled when offer has price categories', () => {
      const contextValues: IndividualOfferContextValues = {
        ...contextValuesBase,
        offer: getIndividualOfferFactory({
          hasStocks: true,
        }),
      }

      renderIndividualOfferNavigation({ contextValues })

      const datesCapacitiesStep = screen.getByText(LABELS.DATES_CAPACITIES)
      expect(datesCapacitiesStep).toBeInTheDocument()
    })

    it('should never display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({ contextValues: contextValuesBase })

      const stockPricesStep = screen.queryByText(LABELS.STOCK_PRICES)
      expect(stockPricesStep).not.toBeInTheDocument()
    })
  })

  describe('when offer is not an event', () => {
    const contextValuesBase = individualOfferContextValuesFactory({
      isEvent: null,
      // TODO (igabriele, 2025-08-05): We shoudn't need to "reset" factories default values.
      offer: offerBase,
    })

    it('should display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({
        contextValues: contextValuesBase,
      })

      const stockStepAsALink = screen.queryByRole('link', {
        name: LABELS.STOCK_PRICES,
      })
      expect(stockStepAsALink).not.toBeInTheDocument()
      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })

    it('should display "Stock & Prix" step as active/enabled when offer is no longer a non-published draft', () => {
      const props: IndividualOfferNavigationProps = {
        isUsefulInformationSubmitted: true,
      }

      renderIndividualOfferNavigation({
        contextValues: contextValuesBase,
        props,
      })

      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })

    it('should display "Stock & Prix" step as active/enabled when offer has stocks', () => {
      const contextValues: IndividualOfferContextValues = {
        ...contextValuesBase,
        isEvent: false,
        offer: {
          ...offerBase,
          hasStocks: true,
        },
      }

      renderIndividualOfferNavigation({ contextValues })

      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })
  })

  describe('on creation mode', () => {
    const contextValuesBase = individualOfferContextValuesFactory({
      isEvent: false,
      offer: offerBase,
    })

    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.CREATION,
    })

    it('should display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      const summaryStepAsALink = screen.queryByRole('link', {
        name: LABELS.SUMMARY,
      })
      expect(summaryStepAsALink).not.toBeInTheDocument()
      const summaryStep = screen.getByText(LABELS.SUMMARY)
      expect(summaryStep).toBeInTheDocument()
    })

    it('should display "Récapitulatif" step as active/enabled when offer has stocks', () => {
      const constextValues = {
        ...contextValuesBase,
        offer: {
          ...offerBase,
          hasStocks: true,
        },
      }

      renderIndividualOfferNavigation({
        contextValues: constextValues,
        path,
      })

      const summaryStep = screen.getByText(LABELS.SUMMARY)
      expect(summaryStep).toBeInTheDocument()
    })

    it('should never display "Réservation" step', () => {
      renderIndividualOfferNavigation({})

      const bookingStep = screen.queryByText(LABELS.BOOKING)
      expect(bookingStep).not.toBeInTheDocument()
    })
  })

  describe('on edition mode', () => {
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    it('should display "Réservation" active/enabled step', () => {
      renderIndividualOfferNavigation({ path })

      expect(
        screen.getByRole('link', { name: LABELS.BOOKING })
      ).toBeInTheDocument()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      expect(
        screen.queryByRole('link', { name: LABELS.SUMMARY })
      ).not.toBeInTheDocument()
    })
  })

  describe('on read-only mode', () => {
    const path = getIndividualOfferPath({
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    it('should display "Réservation" active/enabled step', () => {
      renderIndividualOfferNavigation({ path })

      expect(
        screen.getByRole('link', { name: LABELS.BOOKING })
      ).toBeInTheDocument()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ path })

      expect(
        screen.queryByRole('link', { name: LABELS.SUMMARY })
      ).not.toBeInTheDocument()
    })
  })

  describe('with WIP_ENABLE_NEW_OFFER_CREATION_FLOW feature flag', () => {
    // Will be merged once the feature is enabled in production.
    const FF_LABELS = {
      links: {
        DESCRIPTION: /\d Description/,
        LOCALISATION: /\d Localisation/,
        PRICE_LIST: /\d Tarifs/,
        TIMETABLE: /\d Horaires/,
        SUMMARY: /\d Récapitulatif/,
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

      expect(
        screen.getByRole('link', { name: FF_LABELS.links.DESCRIPTION })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.LOCALISATION })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.PRICE_LIST })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.TIMETABLE })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.SUMMARY })
      ).toBeInTheDocument()
    })

    it('should display the expected steps when the offer is NOT an event', () => {
      const contextValues = individualOfferContextValuesFactory({
        isEvent: false,
      })

      renderIndividualOfferNavigation({ contextValues, options })

      expect(
        screen.getByRole('link', { name: FF_LABELS.links.DESCRIPTION })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.LOCALISATION })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.PRICE_LIST })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('link', { name: FF_LABELS.links.TIMETABLE })
      ).not.toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: FF_LABELS.links.SUMMARY })
      ).toBeInTheDocument()
    })
  })
})
