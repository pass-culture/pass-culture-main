import { MOCKED_BACK_ADDRESS_LABEL } from '../support/constants.js'
import {
  interceptSearch5Adresses,
  logInAndGoToPage,
} from '../support/helpers.ts'

const newVenueName = 'First Venue'

describe('Signup journey with not diffusible offerer siret', () => {
  let login: string
  const mySiret = '92345678912345'

  beforeEach(() => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_new_pro_user',
      (response) => {
        login = response.body.user.email
      }
    )
    cy.intercept({
      method: 'GET',
      url: `/venues/siret/**`,
    }).as('venuesSiret')
    cy.intercept({ method: 'POST', url: '/offerers/new', times: 1 }).as(
      'createOfferer'
    )
    cy.intercept({ method: 'GET', url: '/collective/educational-domains' }).as(
      'getCulturalDomains'
    )
    cy.setFeatureFlags([{ name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true }])
  })

  it('I should be able to sign up with a new account and create a new offerer with a not diffusible siret without an address', () => {
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify a venue with a SIRET' })
    cy.url().should('contain', '/inscription/structure/recherche')
    cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I fill identification form with a public name' })
    cy.url().should('contain', '/inscription/structure/identification')
    cy.findByText(
      'Certaines informations de votre structure ne sont pas diffusibles.'
    ).should('be.visible')
    cy.findByLabelText(/Nom public/).type(newVenueName)
    cy.findByLabelText('Non').click()
    cy.findByLabelText(/Adresse postale/).should('not.exist')
    cy.findByText('Étape suivante').click()
    cy.wait('@getCulturalDomains').its('response.statusCode').should('eq', 200)

    cy.findByLabelText(
      /Sélectionnez un ou plusieurs domaines d’activité/
    ).click()
    cy.findByLabelText(/Théatre/).click()

    cy.findByText('Étape précédente').click()
    cy.findByLabelText('Non').should('be.checked')
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill activity form without target audience' })
    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByLabelText(/Activité principale/).select('Autre')
    cy.findByLabelText('Numéro de téléphone').type('612345678')
    cy.findByText('Au grand public').click()

    cy.findByLabelText(
      /Sélectionnez un ou plusieurs domaines d’activité/
    ).click()
    cy.findByLabelText(/Théatre/).click()

    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/inscription/structure/confirmation')

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })

    cy.findByLabelText(
      'Commencer la création d’offre sur l’application mobile'
    ).should('be.visible')
  })

  it('I should be able to sign up with a new account and create a new offerer with a not diffusible siret with an address', () => {
    interceptSearch5Adresses()
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify a venue with a SIRET' })
    cy.url().should('contain', '/inscription/structure/recherche')
    cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I fill identification form with a public name' })
    cy.url().should('contain', '/inscription/structure/identification')
    cy.findByLabelText(/Nom public/).type(newVenueName)
    cy.findByText('Oui').click()

    cy.findByLabelText(/Adresse postale/).type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()

    cy.findByText('Étape suivante').click()
    cy.findByText('Étape précédente').click()
    cy.findByLabelText('Oui').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill activity form without target audience' })
    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByLabelText(/Activité principale/).select('Galerie d’art')
    cy.findByLabelText('Numéro de téléphone').type('612345678')
    cy.findByText('Au grand public').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/inscription/structure/confirmation')

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })

    cy.findByLabelText(
      'Commencer la création d’offre sur l’application mobile'
    ).should('be.visible')
  })
})

function goToOffererCreation(login: string) {
  cy.stepLog({ message: 'I am logged in' })
  logInAndGoToPage(login, '/')

  cy.stepLog({ message: 'I start offerer creation' })
}
