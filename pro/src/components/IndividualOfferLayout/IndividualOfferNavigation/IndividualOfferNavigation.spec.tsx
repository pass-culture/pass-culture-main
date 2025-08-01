import { screen } from '@testing-library/react'

import { IndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  OFFER_WIZARD_MODE,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
} from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { individualOfferContextValuesFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { IndividualOfferNavigation } from './IndividualOfferNavigation'

type IndividualOfferNavigationTestProps = {
  mode?: OFFER_WIZARD_MODE
  isEvent?: boolean
  isUsefulInformationSubmitted?: boolean
  hasPriceCategories?: boolean
  hasStocks?: boolean
  storeOverrides?: any
  features?: string[]
}

const renderIndividualOfferNavigation = ({
  mode = OFFER_WIZARD_MODE.CREATION,
  isEvent = false,
  isUsefulInformationSubmitted = false,
  hasPriceCategories = false,
  hasStocks = false,
  storeOverrides,
  features = [],
}: IndividualOfferNavigationTestProps = {}) => {
  const contextValues = individualOfferContextValuesFactory({ isEvent })
  if (contextValues.offer) {
    if (!hasPriceCategories) {
      contextValues.offer = {
        ...contextValues.offer,
        priceCategories: [],
      }
    }

    if (!hasStocks) {
      contextValues.offer = {
        ...contextValues.offer,
        hasStocks: false,
      }
    }

    if (!isEvent) {
      contextValues.offer = {
        ...contextValues.offer,
        isEvent: false,
      }
    }
  }

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferNavigation
        isUsefulInformationSubmitted={isUsefulInformationSubmitted}
      />
    </IndividualOfferContext.Provider>,
    {
      storeOverrides,
      initialRouterEntries: [
        getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
          mode,
        }),
      ],
      features,
    }
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
  it('should always display "Détails" and "Informations pratiques" active/enabled steps', () => {
    renderIndividualOfferNavigation()

    const detailsStep = screen.getByRole('link', { name: LABELS.DETAILS })
    expect(detailsStep).toBeInTheDocument()

    const usefulInformationsStep = screen.getByRole('link', {
      name: LABELS.USEFUL_INFORMATIONS,
    })
    expect(usefulInformationsStep).toBeInTheDocument()
  })

  it('should display "Image et vidéo" active step when WIP_ADD_VIDEO is enabled', () => {
    renderIndividualOfferNavigation({
      features: ['WIP_ADD_VIDEO'],
    })

    const mediaStep = screen.getByRole('link', { name: LABELS.MEDIA })
    expect(mediaStep).toBeInTheDocument()
  })

  describe('when offer is an event', () => {
    it('should display "Tarifs" and "Dates & Capacités" steps', () => {
      renderIndividualOfferNavigation({ isEvent: true })

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
      renderIndividualOfferNavigation({
        isEvent: true,
        isUsefulInformationSubmitted: true,
      })

      const pricesStep = screen.getByText(LABELS.PRICES)
      expect(pricesStep).toBeInTheDocument()

      const datesCapacitiesStep = screen.getByText(LABELS.DATES_CAPACITIES)
      expect(datesCapacitiesStep).toBeInTheDocument()
    })

    it('should display "Tarifs" step as active/enabled when offer has price categories', () => {
      renderIndividualOfferNavigation({
        isEvent: true,
        hasPriceCategories: true,
      })

      const pricesStep = screen.getByText(LABELS.PRICES)
      expect(pricesStep).toBeInTheDocument()
    })

    it('should display "Dates et Capacités" step as active/enabled when offer has price categories', () => {
      renderIndividualOfferNavigation({
        isEvent: true,
        hasPriceCategories: true,
      })

      const datesCapacitiesStep = screen.getByText(LABELS.DATES_CAPACITIES)
      expect(datesCapacitiesStep).toBeInTheDocument()
    })

    it('should never display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({
        isEvent: true,
      })

      const stockPricesStep = screen.queryByText(LABELS.STOCK_PRICES)
      expect(stockPricesStep).not.toBeInTheDocument()
    })
  })

  describe('when offer is not an event', () => {
    it('should display "Stock & Prix" step', () => {
      renderIndividualOfferNavigation({ isEvent: false })

      const stockStepAsALink = screen.queryByRole('link', {
        name: LABELS.STOCK_PRICES,
      })
      expect(stockStepAsALink).not.toBeInTheDocument()
      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })

    it('should display "Stock & Prix" step as active/enabled when offer is no longer a non-published draft', () => {
      renderIndividualOfferNavigation({
        isEvent: false,
        isUsefulInformationSubmitted: true,
      })

      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })

    it('should display "Stock & Prix" step as active/enabled when offer has stocks', () => {
      renderIndividualOfferNavigation({
        isEvent: false,
        hasStocks: true,
      })

      const stockStep = screen.getByText(LABELS.STOCK_PRICES)
      expect(stockStep).toBeInTheDocument()
    })
  })

  describe('on creation mode', () => {
    it('should display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.CREATION })

      const summaryStepAsALink = screen.queryByRole('link', {
        name: LABELS.SUMMARY,
      })
      expect(summaryStepAsALink).not.toBeInTheDocument()
      const summaryStep = screen.getByText(LABELS.SUMMARY)
      expect(summaryStep).toBeInTheDocument()
    })

    it('should display "Récapitulatif" step as active/enabled when offer has stocks', () => {
      renderIndividualOfferNavigation({
        mode: OFFER_WIZARD_MODE.CREATION,
        hasStocks: true,
      })

      const summaryStep = screen.getByText(LABELS.SUMMARY)
      expect(summaryStep).toBeInTheDocument()
    })

    it('should never display "Réservation" step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.CREATION })

      const bookingStep = screen.queryByText(LABELS.BOOKING)
      expect(bookingStep).not.toBeInTheDocument()
    })
  })

  describe('on edition mode', () => {
    it('should display "Réservation" active/enabled step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.EDITION })

      const bookingStep = screen.getByText(LABELS.BOOKING)
      expect(bookingStep).toBeInTheDocument()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.EDITION })

      const summaryStep = screen.queryByText(LABELS.SUMMARY)
      expect(summaryStep).not.toBeInTheDocument()
    })
  })

  describe('on read-only mode', () => {
    it('should display "Réservation" active/enabled step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.READ_ONLY })

      const bookingStep = screen.getByText(LABELS.BOOKING)
      expect(bookingStep).toBeInTheDocument()
    })

    it('should never display "Récapitulatif" step', () => {
      renderIndividualOfferNavigation({ mode: OFFER_WIZARD_MODE.READ_ONLY })

      const summaryStep = screen.queryByText(LABELS.SUMMARY)
      expect(summaryStep).not.toBeInTheDocument()
    })
  })
})
