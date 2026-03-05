import { render, screen } from '@testing-library/react'

import { OfferStatus } from '@/apiClient/v1'
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

    it('should render "Offre en cours de validation" when on confirmation page and offer is PENDING', () => {
      const offer = getIndividualOfferFactory({
        status: OfferStatus.PENDING,
      })

      render(
        <IndividualOfferTitle
          mode={OFFER_WIZARD_MODE.CREATION}
          isConfirmationPage={true}
          offer={offer}
        />
      )

      expect(
        screen.getByText('Offre en cours de validation')
      ).toBeInTheDocument()
    })

    it('should render "Offre en cours de validation" when on confirmation page and offer is REJECTED', () => {
      const offer = getIndividualOfferFactory({
        status: OfferStatus.REJECTED,
      })

      render(
        <IndividualOfferTitle
          mode={OFFER_WIZARD_MODE.CREATION}
          isConfirmationPage={true}
          offer={offer}
        />
      )

      expect(
        screen.getByText('Offre en cours de validation')
      ).toBeInTheDocument()
    })

    it('should render "Votre offre a été publiée avec succès" when on confirmation page and offer is PUBLISHED', () => {
      const offer = getIndividualOfferFactory({
        status: OfferStatus.PUBLISHED,
      })

      render(
        <IndividualOfferTitle
          mode={OFFER_WIZARD_MODE.CREATION}
          isConfirmationPage={true}
          offer={offer}
        />
      )

      expect(
        screen.getByText('Votre offre a été publiée avec succès')
      ).toBeInTheDocument()
    })
  })
})
