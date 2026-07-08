import { screen } from '@testing-library/react'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferTitle } from './IndividualOfferTitle'

const renderIndividualOfferTitle = (
  props: Parameters<typeof IndividualOfferTitle>[0],
  features: string[] = []
) => {
  renderWithProviders(<IndividualOfferTitle {...props} />, { features })
}

describe('IndividualOfferTitle', () => {
  describe('when WIP_OFFER_EXPOSURE is disabled', () => {
    it('should render "Modifier l’offre" when mode is EDITION', () => {
      renderIndividualOfferTitle({
        mode: OFFER_WIZARD_MODE.EDITION,
      })

      expect(screen.getByText('Modifier l’offre')).toBeVisible()
    })

    it('should render offer name when mode is READ_ONLY', () => {
      const offer = getIndividualOfferFactory({ name: 'Mon offre incroyable' })
      renderIndividualOfferTitle({
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        offer,
      })

      expect(screen.getByText(offer.name)).toBeVisible()
    })
  })

  describe('when WIP_OFFER_EXPOSURE is enabled', () => {
    it.each([
      OFFER_WIZARD_MODE.EDITION,
      OFFER_WIZARD_MODE.READ_ONLY,
    ])('should render the offer name in %s mode', (mode) => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
      })
      renderIndividualOfferTitle({ mode, offer }, ['WIP_OFFER_EXPOSURE'])

      expect(screen.getByText(offer.name)).toBeVisible()
    })

    it.each([
      OFFER_WIZARD_MODE.EDITION,
      OFFER_WIZARD_MODE.READ_ONLY,
    ])('should render the synchronization tag for a synchronized offer in %s mode', (mode) => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
        lastProvider: { name: 'Boost' },
      })
      renderIndividualOfferTitle({ mode, offer }, ['WIP_OFFER_EXPOSURE'])

      expect(screen.getByText('Synchronisée : Boost')).toBeVisible()
    })

    it('should not render the synchronization tag for a non-synchronized offer', () => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
        lastProvider: undefined,
      })
      renderIndividualOfferTitle(
        {
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          offer,
        },
        ['WIP_OFFER_EXPOSURE']
      )

      expect(screen.queryByText(/Synchronisée/)).not.toBeInTheDocument()
    })
  })

  describe('CREATION mode', () => {
    it('should render "Créer une offre" when not on confirmation page', () => {
      renderIndividualOfferTitle({
        mode: OFFER_WIZARD_MODE.CREATION,
      })

      expect(screen.getByText('Créer une offre')).toBeVisible()
    })
  })
})
