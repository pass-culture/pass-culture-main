import {
  homePageLoaded,
  logInAndSeeDidacticOnboarding,
} from '../support/helpers.ts'

describe('Didactic Onboarding feature', () => {
  let login: string

  beforeEach(() => {
    // order matter here
    cy.intercept({ method: 'GET', url: /\/offers\/categories$/ }).as(
      'getCategories'
    )
    cy.intercept({ method: 'GET', url: /\/offers\/music-types$/ }).as(
      'getMusicTypes'
    )
    cy.intercept({ method: 'GET', url: /\/offers\/\d+\/stocks-stats$/ }).as(
      'getStocksStats'
    )
    cy.intercept({ method: 'GET', url: /\/offers\?.*/ }).as('getOffers')
    cy.intercept({ method: 'GET', url: /\/offers\/\d+\/stocks\/\?.*$/ }).as(
      'getStocks'
    )
    cy.intercept({ method: 'POST', url: /\/offers$/ }).as('postOffer')
    cy.intercept({ method: 'PATCH', url: /\/offers\/\d+$/ }).as('patchOffer')
    cy.intercept({ method: 'PATCH', url: /\/offers\/publish$/ }).as(
      'publishOffer'
    )
    cy.intercept({ method: 'PATCH', url: /\/offers\/\d+\/stocks\/$/ }).as(
      'patchStocks'
    )
    cy.intercept({ method: 'GET', url: /\/offers\/\d+$/ }).as('getOffer')
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

        cy.findByRole('link', { name: 'Manuellement' }).click()
        cy.wait(['@getCategories'])

        cy.stepLog({
          message: `Starts offer creation (before saving a draft)`,
        })

        //  DESCRIPTION STEP
        cy.findByRole('textbox', { name: /Titre de l’offre/ }).type(
          'Mon offre en brouillon'
        )
        cy.findByRole('combobox', { name: /Catégorie/ }).select('Beaux-arts')
        cy.findByLabelText(/Non accessible/).check()
        cy.wait(['@getMusicTypes'])

        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@postOffer'])

        cy.stepLog({
          message: `Go back and resume the previous draft offer`,
        })

        cy.visit('/onboarding/individuel')
        cy.wait(['@getOffers', '@getCategories'])

        cy.findByRole('heading', {
          level: 2,
          name: 'Reprendre une offre déjà commencée',
        })
        cy.findByRole('link', { name: /Mon offre en brouillon/ }).click()
        cy.wait(['@getOffer'])

        cy.findByRole('heading', { level: 1, name: 'Créer une offre' })
        cy.findByRole('textbox', { name: /Titre de l’offre/ }).should(
          'have.value',
          'Mon offre en brouillon'
        )
        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@getMusicTypes', '@patchOffer'])

        //  LOCALISATION STEP
        cy.url().should('contain', '/creation/localisation')

        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@patchOffer'])

        //  MEDIA STEP
        cy.url().should('contain', '/creation/media')
        cy.findByText('Enregistrer et continuer').click()

        //  PRICE CATEGORY STEP
        cy.url().should('contain', '/creation/tarifs')
        cy.wait(['@getStocks'], {
          responseTimeout: 60 * 1000,
        })
        cy.findByLabelText(/Prix/).type('42')

        cy.findByRole('button', { name: 'Enregistrer et continuer' }).click()
        cy.wait(['@patchStocks'])

        //  USEFUL INFO STEP
        cy.url().should('contain', '/creation/informations_pratiques')
        cy.findByText('Enregistrer et continuer').click()
        cy.wait(['@patchOffer'])

        //  SUMMARY STEP
        cy.findByRole('heading', { level: 2, name: 'Description' })
        cy.findByText('Vous y êtes presque !')
        cy.findAllByText('Mon offre en brouillon').should('have.length', 3) // Title is present in the header, in the summary and in the card preview
        cy.findByText('42,00 €')

        cy.stepLog({
          message: `Publishing first offer to get onboarded`,
        })

        cy.findByRole('button', { name: 'Publier l’offre' }).click()
        cy.wait(['@publishOffer'], {
          requestTimeout: 60000 * 2,
          responseTimeout: 60000 * 2,
        })

        cy.findByRole('dialog', {
          name: 'Félicitations, vous avez créé votre offre !',
        })

        cy.visit('/accueil')
        homePageLoaded()
      }
    )
  })
})

function fromOnBoardingGoToCollectiveModal() {
  // Hack because "aller au contenu" is focued by `useFocus`
  cy.findByText('Aller au contenu').click()

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
    'https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage'
  )
}

function fromOnBoardingGoToFirstOfferCreation() {
  cy.stepLog({
    message: 'I start my first offer for the beneficiaries on the mobile app',
  })

  // Hack because "aller au contenu" is focued by `useFocus`
  cy.findByText('Aller au contenu').click()

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
