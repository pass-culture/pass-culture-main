import { screen } from '@testing-library/react'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { describe, expect, it } from 'vitest'

import { ReimbursementWaitingBanner } from './ReimbursementWaitingBanner'

describe('ReimbursementWaitingBanner', () => {
  it('should show valid bank account message and faq link when hasValidBankAccount', () => {
    renderWithProviders(<ReimbursementWaitingBanner hasValidBankAccount />)
    expect(
      screen.getByText(
        /Les remboursements sont effectués toutes les 2 à 3 semaines/i
      )
    ).toBeInTheDocument()
    const faqLink = screen.getByRole('link', {
      name: /Comment fonctionne les remboursements/i,
    })
    expect(faqLink).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4411992051601--Acteurs-Culturels-Quand-votre-prochain-remboursement-sera-t-il-effectu%C3%A9'
    )
  })

  it('should show pending bank account message and internal link when hasPendingBankAccount', () => {
    renderWithProviders(<ReimbursementWaitingBanner hasPendingBankAccount />)
    expect(
      screen.getByText(
        /Vos coordonnées bancaires sont en cours de vérification/i
      )
    ).toBeInTheDocument()
    const link = screen.getByRole('link', {
      name: /Suivre la validation de vos coordonnées bancaires/i,
    })
    expect(link).toHaveAttribute(
      'href',
      '/remboursements/informations-bancaires'
    )
  })

  it('should show no bank account message and internal link when offerer has no registered bank account', () => {
    renderWithProviders(<ReimbursementWaitingBanner />)
    expect(
      screen.getByText(
        /Ajoutez un compte bancaire pour débloquer le remboursement/i
      )
    ).toBeInTheDocument()
    const link = screen.getByRole('link', {
      name: /Ajouter un compte bancaire/i,
    })
    expect(link).toHaveAttribute(
      'href',
      '/remboursements/informations-bancaires'
    )
  })
})
