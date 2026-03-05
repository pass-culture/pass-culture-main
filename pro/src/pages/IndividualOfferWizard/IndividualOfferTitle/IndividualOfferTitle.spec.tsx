import { render, screen } from '@testing-library/react'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { IndividualOfferTitle } from './IndividualOfferTitle'

describe('IndividualOfferTitle', () => {
  it('should render "Modifier l’offre" when mode is EDITION', () => {
    render(
      <IndividualOfferTitle
        mode={OFFER_WIZARD_MODE.EDITION}
        isConfirmationPage={false}
      />
    )

    expect(screen.getByText('Modifier l’offre')).toBeInTheDocument()
  })

  it('should render offer name when mode is READ_ONLY', () => {
    const offer = getIndividualOfferFactory({
      name: 'Mon offre incroyable',
    })
    render(
      <IndividualOfferTitle
        mode={OFFER_WIZARD_MODE.READ_ONLY}
        isConfirmationPage={false}
        offer={offer}
      />
    )

    expect(screen.getByText(offer.name)).toBeInTheDocument()
  })

  describe('CREATION mode', () => {
    it('should render "Créer une offre" when not on confirmation page', () => {
      render(
        <IndividualOfferTitle
          mode={OFFER_WIZARD_MODE.CREATION}
          isConfirmationPage={false}
        />
      )

      expect(screen.getByText('Créer une offre')).toBeInTheDocument()
    })
  })
})
