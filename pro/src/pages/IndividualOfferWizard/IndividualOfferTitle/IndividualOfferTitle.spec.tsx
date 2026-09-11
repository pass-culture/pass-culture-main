import { screen } from '@testing-library/react'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferTitle } from './IndividualOfferTitle'

const renderIndividualOfferTitle = (
  props: Parameters<typeof IndividualOfferTitle>[0]
) => {
  renderWithProviders(<IndividualOfferTitle {...props} />)
}

describe('IndividualOfferTitle', () => {
  describe('EDITION mode', () => {
    it('should render the offer name', () => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
      })
      renderIndividualOfferTitle({ mode: OFFER_WIZARD_MODE.EDITION, offer })

      expect(screen.getByText(offer.name)).toBeVisible()
    })

    it('should render the synchronization tag for a synchronized offer', () => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
        lastProvider: { name: 'Boost' },
      })
      renderIndividualOfferTitle({ mode: OFFER_WIZARD_MODE.EDITION, offer })

      expect(screen.getByText('Synchronisée : Boost')).toBeVisible()
    })

    it('should not render the synchronization tag for a non-synchronized offer', () => {
      const offer = getIndividualOfferFactory({
        name: 'Mon offre incroyable',
        lastProvider: undefined,
      })
      renderIndividualOfferTitle({
        mode: OFFER_WIZARD_MODE.EDITION,
        offer,
      })

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
