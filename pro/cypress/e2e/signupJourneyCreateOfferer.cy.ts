import {
  DEFAULT_AXE_CONFIG,
  DEFAULT_AXE_RULES,
  MOCKED_BACK_ADDRESS_LABEL,
} from '../support/constants.ts'
import {
  interceptSearch5Adresses,
  logInAndGoToPage,
} from '../support/helpers.ts'

const newVenueName = 'First Venue'

describe('Signup journey with unknown offerer and unknown venue', () => {
  let login: string
  const mySiret = '12345678912345'

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
    cy.intercept({
      method: 'GET',
      url: '/venue-types',
      times: 1,
    }).as('venue-types')
    cy.intercept({ method: 'POST', url: '/offerers/new', times: 1 }).as(
      'createOfferer'
    )
    cy.setFeatureFlags([
      { name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true },
      { name: 'WIP_2025_AUTOLOGIN', isActive: true },
    ])
  })

  it('I should be able to sign up with a new account and create a new offerer with an unknown SIREN (unknown SIRET)', () => {
    goToOffererCreation(login)

    cy.stepLog({ message: 'I specify a venue with a SIRET' })
    cy.url().should('contain', '/inscription/structure/recherche')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

    cy.stepLog({ message: 'I fill identification form with a public name' })
    cy.url().should('contain', '/inscription/structure/identification')
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.findByLabelText('Nom public').type(newVenueName)
    // Make the venue open to public.
    cy.findByText('Oui').click()

    cy.findByText('Étape suivante').click()
    cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I fill activity form without target audience' })
    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByLabelText('Activité principale *').select('Spectacle vivant')
    cy.findByLabelText('Numéro de téléphone').type('612345678')
    cy.findByText('Étape suivante').click()
    cy.findByText('Veuillez sélectionner une des réponses ci-dessus')

    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByText('Au grand public').click()
    cy.stepLog({ message: 'I fill in missing target audience' })
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/inscription/structure/confirmation')

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })

    fromOnBoardingPublishMyFirstOffer()

    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    cy.contains(
      'Votre structure est en cours de traitement par les équipes du pass Culture'
    ).should('be.visible')
    cy.findByText(newVenueName).should('be.visible')
  })
})

describe('Signup journey with known offerer...', () => {
  let login: string
  let mySiret: string

  beforeEach(() => {
    cy.visit('/')
    cy.intercept({ method: 'POST', url: '/offerers/new', times: 1 }).as(
      'createOfferer'
    )
    cy.intercept({
      method: 'GET',
      url: '/venue-types',
      times: 1,
    }).as('venue-types')
    interceptSearch5Adresses()
    cy.intercept({
      method: 'GET',
      url: `/venues/siret/**`,
    }).as('venuesSiret')
    cy.setFeatureFlags([
      { name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true },
      { name: 'WIP_2025_AUTOLOGIN', isActive: true },
    ])
  })

  describe('...and unknown venue', () => {
    let siren: string
    const endSiret = '12345'
    beforeEach(() => {
      cy.visit('/connexion')
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_new_pro_user_and_offerer',
        (response) => {
          login = response.body.user.email
          siren = response.body.siren
          mySiret = siren + endSiret
        }
      )
      cy.setFeatureFlags([{ name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true }])
    })

    it('I should be able to sign up with a new account and create a new venue with a known SIREN (unknown SIRET)', () => {
      goToOffererCreation(login)

      cy.stepLog({ message: 'I specify a venue with a SIRET' })
      cy.url().should('contain', '/inscription/structure/recherche')
      cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
      cy.findByText('Continuer').click()
      cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I fill identification form with a public name' })
      cy.url().should('contain', '/inscription/structure/identification')
      cy.findByLabelText('Nom public').type(newVenueName)
      // Make the venue open to public.
      cy.findByText('Oui').click()

      cy.findByText('Étape suivante').click()
      cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I fill completely activity form' })
      cy.url().should('contain', '/inscription/structure/activite')
      cy.findByLabelText('Activité principale *').select('Spectacle vivant')
      cy.findByLabelText('Numéro de téléphone').type('612345678')
      cy.findByText('Au grand public').click()
      cy.findByText('Étape suivante').click()

      cy.stepLog({ message: 'the next step is displayed' })
      cy.url().should('contain', '/inscription/structure/confirmation')

      cy.stepLog({ message: 'I validate the registration' })
      cy.findByText('Valider et créer ma structure').click()
      cy.wait('@createOfferer')

      cy.stepLog({ message: 'the offerer is created' })
      cy.visit('/accueil')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

      cy.contains(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      ).should('be.visible')
      cy.findByText(newVenueName).should('not.exist')
    })
  })

  describe('...and known venue', () => {
    beforeEach(() => {
      cy.visit('/connexion')
      cy.sandboxCall(
        'GET',
        'http://localhost:5001/sandboxes/pro/create_new_pro_user_and_offerer_with_venue',
        (response) => {
          login = response.body.user.email
          mySiret = response.body.siret
        }
      )
      interceptSearch5Adresses()
      cy.intercept({ method: 'POST', url: '/offerers' }).as('postOfferers')
      cy.setFeatureFlags([{ name: 'WIP_IS_OPEN_TO_PUBLIC', isActive: true }])
    })

    it('I should be able as a local authority to sign up with a new account and a known offerer/venue and then create a new venue in the space', () => {
      goToOffererCreation(login)

      cy.stepLog({ message: 'I specify an offerer with a SIRET' })
      cy.url().should('contain', '/inscription/structure/recherche')
      cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
      cy.findByText('Continuer').click()
      cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I add a new offerer' })
      cy.url().should('contain', '/inscription/structure/rattachement')

      cy.findByText('Ajouter une nouvelle structure').click()
      cy.wait('@search5Address')

      cy.stepLog({ message: 'I fill identification form with a new address' })
      cy.url().should('contain', '/inscription/structure/identification')
      cy.findByLabelText(/Adresse postale/).clear()
      cy.findByLabelText(/Adresse postale/).invoke(
        'val',
        MOCKED_BACK_ADDRESS_LABEL.slice(0, MOCKED_BACK_ADDRESS_LABEL.length - 1)
      ) // To avoid being spammed by address search on each chars typed
      cy.findByLabelText(/Adresse postale/).type('s') // previous search was too fast, this one raises suggestions
      cy.wait('@search5Address')
      cy.findByRole('option', { name: MOCKED_BACK_ADDRESS_LABEL }).click()
      // Make the venue open to public.
      cy.findByText('Oui').click()

      cy.findByText('Étape suivante').click()
      cy.wait('@venue-types').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I fill activity form without main activity' })
      cy.url().should('contain', '/inscription/structure/activite')
      cy.findByLabelText('Activité principale *').select(
        'Sélectionnez votre activité principale'
      ) // No activity selected
      cy.findByLabelText('Numéro de téléphone').type('612345678')
      cy.findByText('Au grand public').click()
      cy.findByText('Étape suivante').click()
      cy.findByTestId('error-venueTypeCode').contains(
        'Veuillez sélectionner une activité principale'
      )

      cy.stepLog({ message: 'I fill in missing main activity' })
      cy.url().should('contain', '/inscription/structure/activite')
      cy.findByLabelText('Activité principale *').select('Spectacle vivant')
      cy.findByText('Étape suivante').click()

      cy.stepLog({ message: 'the next step is displayed' })
      cy.url().should('contain', '/inscription/structure/confirmation')

      cy.stepLog({ message: 'I validate the registration' })

      cy.findByText('Valider et créer ma structure').click()
      cy.wait('@createOfferer')

      cy.stepLog({ message: 'the offerer is created' })
      cy.visit('/accueil')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

      cy.stepLog({ message: 'the attachment is in progress' })
      cy.contains(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      ).should('be.visible')
    })

    it('I should be able to sign up with a new account and a known offerer/venue and then join the space', () => {
      goToOffererCreation(login)

      cy.stepLog({ message: 'I specify an offerer with a SIRET' })
      cy.url().should('contain', '/inscription/structure/recherche')
      cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
      cy.findByText('Continuer').click()
      cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

      cy.stepLog({ message: 'I chose to join the space' })
      cy.contains('Rejoindre cet espace').click()

      cy.findByTestId('confirm-dialog-button-confirm').click()
      cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)
      cy.contains('Accéder à votre espace').click()

      cy.stepLog({ message: 'I am redirected to homepage' })
      cy.url({ timeout: 10000 }).should('contain', '/accueil')
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

      // TODO: Find a better way to wait for the offerer to be created
      cy.reload()

      cy.stepLog({ message: 'the attachment is in progress' })
      cy.contains(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      ).should('be.visible')
    })
  })
})

function goToOffererCreation(login: string) {
  cy.stepLog({ message: 'I am logged in' })
  logInAndGoToPage(login, '/')

  cy.stepLog({ message: 'I start offerer creation' })
}

function fromOnBoardingPublishMyFirstOffer() {
  cy.stepLog({
    message: 'I start my first offer for the beneficiaries on the mobile app',
  })
  cy.findByLabelText(
    'Commencer la création d’offre sur l’application mobile'
  ).click()
  cy.findByRole('heading', {
    level: 1,
    name: 'Offre à destination des jeunes',
  })
  cy.findByRole('heading', {
    level: 2,
    name: 'Comment souhaitez-vous créer votre 1ère offre ?',
  })

  // Choose to create the first offer manually
  cy.findByRole('link', { name: 'Manuellement' }).click()

  // --------------
  // Offer creation
  // --------------

  cy.stepLog({
    message: `Starts offer creation`,
  })

  // Starts offer creation by choosing offer type
  cy.findByRole('radiogroup', { name: 'Votre offre est' })
    .findByText('Un bien physique')
    .click()
  cy.findByRole('button', { name: 'Étape suivante' }).click()

  // ---------------------
  // Step 1: Offer details
  // ---------------------

  cy.intercept('POST', 'http://localhost:5001/offers/draft').as(
    'postOfferDraft'
  )

  cy.findByRole('textbox', { name: /Titre de l’offre/ }).type(
    'Mon offre en brouillon'
  )

  cy.findByRole('combobox', { name: /Catégorie/ }).select('Beaux-arts')

  // Saving a draft
  cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()

  cy.wait('@postOfferDraft')

  // ---------------------------
  // Step 2: Useful informations
  // ---------------------------

  cy.intercept('PATCH', 'http://localhost:5001/offers/1').as('patchOffer')

  // Minimal required fields are already filled by default in this step, so we can directly go to the next step
  // TODO (igabriele,  2025-08-04): Investigate this wait (it may attempt to click during an unecessary re-render).
  // eslint-disable-next-line cypress/no-unnecessary-waiting
  cy.wait(250)
    .findByRole('button', { name: 'Enregistrer et continuer' })
    .click()

  cy.wait('@patchOffer')

  // ----------------------
  // Step 3: Stock & Prices
  // ----------------------

  // Set price
  cy.findByLabelText(/Prix/).type('42')

  cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()

  // -----------------------
  // Step 4: Details summary
  // -----------------------

  cy.findByRole('heading', { level: 2, name: 'Détails de l’offre' })
  cy.findByText('Vous y êtes presque !')
  cy.findAllByText('Mon offre en brouillon').should('have.length', 3) // Title is present in the header, in the summary and in the card preview
  cy.findByText('42,00 €')

  cy.stepLog({
    message: `Publishing first offer to get onboarded`,
  })

  // Publish offer
  cy.findByRole('button', { name: 'Publier l’offre' }).click()

  // Expect congratulations dialog
  cy.findByRole('dialog', {
    name: 'Félicitations, vous avez créé votre offre !',
  })

  // Navigate to banking information page
  cy.findByRole('button', { name: 'Plus tard' }).click()
}
