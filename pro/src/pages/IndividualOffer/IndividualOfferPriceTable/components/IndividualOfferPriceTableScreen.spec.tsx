import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import {
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { IndividualOfferPriceTableScreen } from './IndividualOfferPriceTableScreen'

vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.CREATION),
}))

interface ScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
  offerStocks: GetOfferStockResponseModel[]
}
const renderPriceTableScreen: RenderComponentFunction<
  ScreenProps,
  IndividualOfferContextValues
> = (params) => {
  const offer = getIndividualOfferFactory({
    id: 10,
    isEvent: false,
    isDigital: false,
    subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
  })
  const contextValues: IndividualOfferContextValues = {
    categories: [],
    hasPublishedOfferWithSameEan: false,
    isEvent: null,
    setIsEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    offer,
    offerId: offer.id,
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }
  const props: ScreenProps = {
    offer,
    offerStocks: [],
    ...params.props,
  }
  contextValues.offer = props.offer ?? contextValues.offer

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferPriceTableScreen {...props} />
    </IndividualOfferContext.Provider>,
    options
  )
}

const LABELS = {
  section: 'Tarifs',
  duoSection: 'Réservations “Duo”',
  addRate: 'Ajouter un tarif',
  price: /Prix/,
  stock: /Stock/,
  duoCheckbox: 'Réservations “Duo”',
  saveAndContinue: 'Enregistrer et continuer',
  saveEdition: 'Enregistrer les modifications',
  nonRefundable: 'Cette offre ne sera pas remboursée',
}

describe('<IndividualOfferPriceTableScreen />', () => {
  describe('creation mode non-event offer', () => {
    it('should render and pass a11y', async () => {
      const { container } = renderPriceTableScreen({})

      expect(
        await screen.findByRole('heading', { name: LABELS.section })
      ).toBeInTheDocument()

      expect(
        //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
        await axe(container, {
          rules: { 'color-contrast': { enabled: false } },
        })
      ).toHaveNoViolations()

      expect(
        screen.getByRole('spinbutton', { name: LABELS.stock })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('spinbutton', { name: LABELS.price })
      ).toBeInTheDocument()
    })

    it('should disable form when offer disabled by context flag', async () => {
      renderPriceTableScreen({
        contextValues: { hasPublishedOfferWithSameEan: true },
      })

      const stockInput = await screen.findByRole('spinbutton', {
        name: LABELS.stock,
      })
      expect(stockInput).toBeDisabled()
    })
  })

  describe('creation mode event offer', () => {
    beforeEach(() => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    })

    it('should show add rate button and not show stock input', async () => {
      const offer = getIndividualOfferFactory({
        id: 11,
        isEvent: true,
        isDigital: false,
        subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
      })

      renderPriceTableScreen({ props: { offer, offerStocks: [] } })

      expect(
        await screen.findByRole('button', { name: LABELS.addRate })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('spinbutton', { name: LABELS.stock })
      ).not.toBeInTheDocument()
    })
  })

  describe('digital non-event offer', () => {
    it('should display activation code callout and activation code button', async () => {
      const offer = getIndividualOfferFactory({
        id: 12,
        isEvent: false,
        isDigital: true,
        subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
      })

      renderPriceTableScreen({ props: { offer, offerStocks: [] } })

      // tooltip button for activation codes
      expect(
        await screen.findByRole('button', {
          name: "Ajouter des codes d'activation",
        })
      ).toBeInTheDocument()
    })
  })

  describe('non reimbursable subcategory', () => {
    it('should show non refundable callout', async () => {
      const offer = getIndividualOfferFactory({
        id: 13,
        isEvent: false,
        isDigital: false,
        subcategoryId: MOCKED_SUBCATEGORY.NON_REFUNDABLE.id,
      })

      renderPriceTableScreen({ props: { offer, offerStocks: [] } })

      expect(
        await screen.findByText(/ne sera pas remboursée|non remboursée/i)
      ).toBeInTheDocument()
    })
  })

  describe('edition mode navigation', () => {
    beforeEach(() => {
      vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    })

    it('should show edition buttons (Annuler et quitter + Enregistrer les modifications)', async () => {
      const offer = getIndividualOfferFactory({
        id: 14,
        isEvent: false,
        isDigital: false,
        subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_OFFLINE.id,
      })

      renderPriceTableScreen({ props: { offer, offerStocks: [] } })

      expect(
        await screen.findByRole('button', { name: 'Annuler et quitter' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: LABELS.saveEdition })
      ).toBeInTheDocument()
    })
  })

  it('should display the duo checkbox if the offer subcatefory can be duo', async () => {
    renderPriceTableScreen({
      props: {
        offer: getIndividualOfferFactory({
          subcategoryId: MOCKED_SUBCATEGORY.CAN_BE_DUO.id,
        }),
      },
    })

    expect(
      await screen.findByRole('heading', { name: LABELS.section })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('checkbox', { name: /Accepter les réservations “Duo“/ })
    ).toBeInTheDocument()
  })
})
