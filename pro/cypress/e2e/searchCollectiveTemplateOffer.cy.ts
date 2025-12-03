import { DEFAULT_AXE_CONFIG, DEFAULT_AXE_RULES } from '../support/constants.ts'
import { logInAndGoToPage } from '../support/helpers.ts'

describe('Recherche offres templates collectives', () => {
  let offerPublished: { name: string; venueName: string }
  let offerDraft: { name: string; venueName: string }
  let offerArchived: { name: string; venueName: string }
  let offerUnderReview: { name: string; venueName: string }
  let offerRejected: { name: string; venueName: string }

  beforeEach(() => {
    cy.intercept({ method: 'GET', url: '/collective/offers-template*' }).as(
      'collectiveOffersTemplates'
    )
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_pro_user_with_collective_offer_templates',
      (response) => {
        offerPublished = response.body.offerPublished
        offerDraft = response.body.offerDraft
        offerArchived = response.body.offerArchived
        offerUnderReview = response.body.offerUnderReview
        offerRejected = response.body.offerRejected
        logInAndGoToPage(response.body.user.email, '/accueil')
        cy.visit('/offres/vitrines')
        cy.wait('@collectiveOffersTemplates')
        cy.findAllByTestId('spinner').should('not.exist')
      }
    )
  })

  it('Je peux rechercher par nom et voir le résultat attendu', () => {
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByLabelText(/Nom de l’offre/).type(offerPublished.name)
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
      .its('response.statusCode')
      .should('eq', 200)
    cy.contains(offerPublished.name)
    cy.contains('publiée')
  })

  it('Je peux rechercher par localisation et voir le résultat attendu', () => {
    cy.findByText('Filtrer').click()
    cy.findByLabelText('Localisation').select('En établissement scolaire')
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.contains(offerArchived.name)
    cy.contains('archivée')
  })

  it('Je peux rechercher par format "Atelier de pratique" et voir le résultat attendu', () => {
    cy.findByText('Filtrer').click()
    cy.findByLabelText('Format').select('Atelier de pratique')
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.contains(offerPublished.name)
    cy.contains('publiée')
  })

  it('Je peux rechercher par format "Représentation" et voir le résultat attendu', () => {
    cy.findByText('Filtrer').click()
    cy.findByLabelText('Format').select('Représentation')
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.contains(offerDraft.name)
    cy.contains('brouillon')
    cy.contains(offerUnderReview.name)
    cy.contains('instruction')
    cy.contains(offerRejected.name)
    cy.contains('non conforme')
  })

  it('Je peux rechercher par statut "Publiée" et voir le résultat attendu', () => {
    cy.findByText('Filtrer').click()
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByText('Publiée sur ADAGE').click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.contains(offerPublished.name)
    cy.contains('publiée')
  })

  it('Je peux rechercher par statut "Brouillon" et voir le résultat attendu', () => {
    cy.findByText('Filtrer').click()
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByText('Brouillon').click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.contains(offerDraft.name)
    cy.contains('brouillon')
  })

  it('Je peux combiner plusieurs filtres et réinitialiser', () => {
    cy.findByText('Filtrer').click()
    cy.findByLabelText('Localisation').select('En établissement scolaire')
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByText('En instruction').click()
    cy.findByText('Non conforme').click()
    cy.findByText('Rechercher').click()
    cy.wait('@collectiveOffersTemplates')
    cy.findByText('Aucune offre trouvée pour votre recherche')
    cy.findByText('Réinitialiser les filtres').click()
    cy.findByRole('button', { name: 'Statut' }).click()
    cy.findByText('En instruction').should('not.be.checked')
    cy.findByText('Non conforme').should('not.be.checked')
    cy.findByRole('combobox', { name: /Localisation/ })
      .invoke('val')
      .should('eq', 'all')
    cy.findByRole('combobox', { name: /Format/ })
      .invoke('val')
      .should('eq', 'all')
    cy.findByLabelText(/Nom de l’offre/).clear()
    cy.findByText('Rechercher').click()
    cy.contains(offerPublished.name)
    cy.contains(offerDraft.name)
    cy.contains(offerArchived.name)
    cy.contains(offerUnderReview.name)
    cy.contains(offerRejected.name)
  })
})
