import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { EndBanner } from './EndBanner'

describe('EndBanner', () => {
  describe('lessThan48h variant', () => {
    it('should display the correct message', () => {
      renderWithProviders(<EndBanner offerId={2} variant="lessThan48h" />)

      expect(
        screen.getByText(
          'Nous espérons que votre évènement s’est bien déroulé. Si besoin, vous pouvez annuler la réservation ou modifier à la baisse le prix ou le nombre de participants jusqu’à 48 heures après la date de l’évènement.'
        )
      ).toBeInTheDocument()
    })

    it('should display the correct link', () => {
      renderWithProviders(<EndBanner offerId={2} variant="lessThan48h" />)

      const link = screen.getByRole('link', {
        name: "Modifier à la baisse le prix ou le nombre d'élèves",
      })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', '/offre/2/collectif/stocks/edition')
    })
  })

  describe('moreThan48h variant', () => {
    it('should display the correct message', () => {
      renderWithProviders(<EndBanner offerId={5} variant="moreThan48h" />)

      expect(
        screen.getByText(
          'Les remboursements sont effectués toutes les 2 à 3 semaines. Vous serez notifié par mail une fois que le remboursement aura été versé.'
        )
      ).toBeInTheDocument()
    })

    it('should display the correct external link', () => {
      renderWithProviders(<EndBanner offerId={5} variant="moreThan48h" />)

      const link = screen.getByText('Comment fonctionne les remboursements ?')

      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute(
        'href',
        'https://aide.passculture.app/hc/fr/articles/4411992051601--Acteurs-Culturels-Quand-votre-prochain-remboursement-sera-t-il-effectu%C3%A9'
      )
    })
  })

  describe('moreThan48hWithoutBankInformation variant', () => {
    it('should display the correct message', () => {
      renderWithProviders(
        <EndBanner offerId={10} variant="moreThan48hWithoutBankInformation" />
      )

      expect(
        screen.getByText(
          'Ajoutez un compte bancaire pour débloquer le remboursement.'
        )
      ).toBeInTheDocument()
    })

    it('should display the correct link', () => {
      renderWithProviders(
        <EndBanner offerId={10} variant="moreThan48hWithoutBankInformation" />
      )

      const link = screen.getByText('Ajouter un compte bancaire')

      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute(
        'href',
        '/remboursements/informations-bancaires'
      )
    })
  })

  describe('offerId replacement', () => {
    it('should replace {offerId} placeholder in link href', () => {
      renderWithProviders(<EndBanner offerId={123} variant="lessThan48h" />)

      const link = screen.getByText(
        "Modifier à la baisse le prix ou le nombre d'élèves"
      )

      expect(link).toHaveAttribute(
        'href',
        '/offre/123/collectif/stocks/edition'
      )
    })

    it('should handle different offerId values correctly', () => {
      renderWithProviders(<EndBanner offerId={999} variant="lessThan48h" />)

      const link = screen.getByRole('link', {
        name: "Modifier à la baisse le prix ou le nombre d'élèves",
      })
      expect(link).toHaveAttribute(
        'href',
        '/offre/999/collectif/stocks/edition'
      )
    })
  })
})
