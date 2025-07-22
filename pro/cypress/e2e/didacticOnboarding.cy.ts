import {
  homePageLoaded,
  logInAndSeeDidacticOnboarding,
} from '../support/helpers.ts'

describe('Didactic Onboarding feature', () => {
  let login: string

  beforeEach(() => {
    cy.intercept({ method: 'POST', url: '/offers/draft' }).as('postDraftOffer')
    cy.intercept({ method: 'PATCH', url: '/offers/draft/*' }).as(
      'patchDraftOffer'
    )
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
  })

  it('I should not be able to onboard me by submitting an Adage referencing file if I don’t have an Adage ID', () => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email

        // Should display the didactic onboarding homepage after login
        logInAndSeeDidacticOnboarding(login)

        // From the onboarding page, navigate to the collective modal
        fromOnBoardingGoToCollectiveModal()

        // Check if a file already have been filed by requesting the API, which shouldn't be the case here by default
        cy.stepLog({
          message: `I check my eligibility status which shoud not be onboarded`,
        })
        cy.intercept({ method: 'GET', url: '/offerers/*/eligibility' }).as(
          'getEligibility'
        )

        // Expect to see a message saying that no file have been filed yet
        cy.findByRole('button', { name: /J’ai déposé un dossier/ }).click()
        cy.wait('@getEligibility')
        cy.findByText('Aucun dossier n’a été déposé par votre structure.')
      }
    )
  })

  it('I should be able to onboard me by submitting an Adage referencing file if I have an Adage ID', () => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email

        // Should display the didactic onboarding homepage after login
        logInAndSeeDidacticOnboarding(login)

        // From the onboarding page, navigate to the collective modal
        fromOnBoardingGoToCollectiveModal()

        // Check if a file already have been filed by requesting the API, which shouldn't be the case here by default
        cy.stepLog({
          message: `I check my eligibility status which should be onboarded (via mock)`,
        })
        cy.intercept(
          { method: 'GET', url: '/offerers/*/eligibility' },
          (req) => {
            // Get offerer ID from the URL
            const offererId = req.url.match(/\/offerers\/(\d+)\//)![1]
            // Mock response with an onboarded status to True
            req.reply({
              statusCode: 200,
              body: {
                offererId,
                hasAdageId: true,
                hasDsApplication: null,
                isOnboarded: true,
              },
            })
          }
        ).as('getEligibility')

        // Expect to be redirected to the homepage after have succeeded to check the eligibility
        cy.findByRole('button', { name: /J’ai déposé un dossier/ }).click()
        cy.wait('@getEligibility')
        cy.url().should('contain', '/accueil')
        homePageLoaded()
      }
    )
  })

  it('I should be able to create my first offer automatically', () => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email

        // Should display the didactic onboarding homepage after login
        logInAndSeeDidacticOnboarding(login)

        // From the onboarding page, navigate to the first offer creation
        fromOnBoardingGoToFirstOfferCreation()

        // Choose to create the first offer automatically (which should redirect to venues settings to handle synchronization)
        cy.findByRole('link', { name: 'Automatiquement' }).click()
        cy.url().should('match', /\/structures\/\d+\/lieux\/\d+\/parametres$/)
        cy.findByRole('heading', { level: 1, name: 'Paramètres généraux' })
        cy.findByRole('heading', {
          level: 2,
          name: 'Gestion des synchronisations',
        })
      }
    )
  })

  it('I should be able to start my first offer manually, saving and resume a draft offer, and publish it to get onboarded', () => {
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email

        // Should display the didactic onboarding homepage after login
        logInAndSeeDidacticOnboarding(login)

        // From the onboarding page, navigate to the first offer creation
        fromOnBoardingGoToFirstOfferCreation()

        // Choose to create the first offer manually
        cy.findByRole('link', { name: 'Manuellement' }).click()

        // --------------
        // Offer creation
        // --------------

        cy.stepLog({
          message: `Starts offer creation (before saving a draft)`,
        })

        // Starts offer creation by choosing offer type
        cy.findByRole('group', { name: 'Votre offre est' })
          .findByText('Un bien physique')
          .click()
        cy.findByRole('button', { name: 'Étape suivante' }).click()

        // ---------------------
        // Step 1: Offer details
        // ---------------------

        cy.findByRole('textbox', { name: /Titre de l’offre/ }).type(
          'Mon offre en brouillon'
        )

        cy.findByRole('combobox', { name: /Catégorie/ }).select('Beaux-arts')

        // Saving a draft
        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@getOffer', '@postDraftOffer'])
        cy.findByText('Brouillon enregistré')

        // --------------------
        // Draft – Resume offer
        // --------------------

        cy.stepLog({
          message: `Go back and resume the previous draft offer`,
        })

        // Go back to the onboarding page
        cy.visit('/onboarding/individuel')

        // Expect here to see the draft offer, that we can resume
        cy.findByRole('heading', {
          level: 2,
          name: 'Reprendre une offre déjà commencée',
        })
        cy.findByRole('link', { name: /Mon offre en brouillon/ }).click()

        // ------------------------------------------
        // Step 1: Offer details (resumed from draft)
        // ------------------------------------------

        cy.findByRole('heading', { level: 1, name: 'Créer une offre' })
        cy.findByRole('textbox', { name: /Titre de l’offre/ }).should(
          'have.value',
          'Mon offre en brouillon'
        )
        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@getOffer', '@patchDraftOffer'])

        // ---------------------------
        // Step 2: Useful informations
        // ---------------------------

        // Minimal required fields are already filled by default in this step, so we can directly go to the next step
        cy.url().should('contain', '/creation/pratiques')
        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@getOffer', '@patchOffer'])

        // ----------------------
        // Step 3: Stock & Prices
        // ----------------------

        // Set price
        cy.url().should('contain', '/creation/stocks')
        cy.findByTestId('input-price').type('42')

        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@getOffer', '@patchOffer'])

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
        cy.wait(['@publishOffer', '@getOffer'], {
          requestTimeout: 60000 * 2,
          responseTimeout: 60000 * 2,
        })

        // Expect congratulations dialog
        cy.findByRole('dialog', {
          name: 'Félicitations, vous avez créé votre offre !',
        })

        // Then, check if we can display the homepage (as we are now onboarded)
        cy.visit('/accueil')
        homePageLoaded()
      }
    )
  })
})

function fromOnBoardingGoToCollectiveModal() {
  // Display modal
  cy.stepLog({ message: `I open the referencing modal for teachers` })
  cy.findByLabelText('Commencer la création d’offre sur ADAGE').click()
  cy.findByRole('heading', { level: 1, name: 'Quelles sont les étapes ?' })

  // Check if link for submitting a file is present and correct
  cy.findByRole('link', { name: /Déposer un dossier/ }).should(
    'have.attr',
    'target',
    '_blank'
  )
  cy.findByRole('link', { name: /Déposer un dossier/ }).should(
    'have.attr',
    'href',
    'https://www.demarches-simplifiees.fr/commencer/demande-de-referencement-sur-adage'
  )
}

function fromOnBoardingGoToFirstOfferCreation() {
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
}
