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
    cy.findByLabelText(/Activité principale/).select('Galerie d’art')
    cy.findByLabelText('Numéro de téléphone').type('612345678')
    cy.findByText('Étape suivante').click()
    cy.findByText('Veuillez sélectionner au moins une option')

    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByText('Au grand public').click()
    cy.stepLog({ message: 'I fill in missing target audience' })
    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'the next step is displayed' })
    cy.url().should('contain', '/inscription/structure/confirmation')

    cy.findByText('5 Rue Curial, 75019 Paris')

    cy.injectAxe(DEFAULT_AXE_CONFIG)
    cy.checkA11y(undefined, DEFAULT_AXE_RULES, cy.a11yLog)

    cy.stepLog({ message: 'I validate the registration' })

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })

    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    cy.contains('Où souhaitez-vous diffuser votre première offre ?').should(
      'be.visible'
    )
  })

  it('I should be able to sign up with a new account and create a new offerer with an unknown SIREN (unknown SIRET) and a custom address', () => {
    interceptSearch5Adresses()

    goToOffererCreation(login)

    cy.findByLabelText(/Numéro de SIRET à 14 chiffres/).type(mySiret)
    cy.findByText('Continuer').click()
    cy.wait('@venuesSiret').its('response.statusCode').should('eq', 200)

    cy.findByLabelText('Nom public').type(newVenueName)
    cy.findByText('Oui').click()

    cy.findByText('Vous ne trouvez pas votre adresse ?').click()
    cy.findAllByLabelText(/Adresse postale/)
      .last()
      .type('10 Rue du test')
    cy.findAllByLabelText(/Code postal/).type('75002')
    cy.findAllByLabelText(/Ville/).type('Paris')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText(/Coordonnées GPS/)
      .type('48.853320, 2.348979')
      .blur()
    cy.findByText('Contrôlez la précision de vos coordonnées GPS.').should(
      'be.visible'
    )

    cy.findByText('Étape suivante').click()

    cy.url().should('contain', '/inscription/structure/activite')
    cy.findByLabelText(/Activité principale/).select('Galerie d’art')
    cy.findByLabelText('Numéro de téléphone').type('612345678')
    cy.findByText('Au grand public').click()
    cy.findByText('Étape suivante').click()
    cy.url().should('contain', '/inscription/structure/confirmation')

    cy.findByText('10 Rue du test, 75002 Paris')

    cy.findByText('Valider et créer ma structure').click()
    cy.wait('@createOfferer')

    cy.stepLog({ message: 'the offerer is created' })

    cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')

    cy.contains('Où souhaitez-vous diffuser votre première offre ?').should(
      'be.visible'
    )
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

      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
      cy.location('pathname', { timeout: 30 * 1000 }).should(
        'eq',
        '/rattachement-en-cours'
      )
      cy.contains(
        'Votre rattachement est en cours de traitement par les équipes du pass Culture'
      ).should('be.visible')
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

      // Hack because "aller au contenu" is focued by `useFocus`
      cy.findByRole('link', { name: /Aller au contenu/ })
        .focus()
        .click()

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
      cy.findByLabelText(/Activité principale/).select(
        'Sélectionnez votre activité principale'
      ) // No activity selected
      cy.findByLabelText('Numéro de téléphone').type('612345678')
      cy.findByText('Au grand public').click()
      cy.findByText('Étape suivante').click()
      cy.findByText('Activité non valide')

      cy.stepLog({ message: 'I fill in missing main activity' })
      cy.url().should('contain', '/inscription/structure/activite')
      cy.findByLabelText(/Activité principale/).select('Galerie d’art')
      cy.findByText('Étape suivante').click()

      cy.stepLog({ message: 'the next step is displayed' })
      cy.url().should('contain', '/inscription/structure/confirmation')

      cy.stepLog({ message: 'I validate the registration' })

      cy.findByText('Valider et créer ma structure').click()
      cy.wait('@createOfferer')

      cy.stepLog({ message: 'the offerer is created' })
      cy.findAllByTestId('spinner', { timeout: 30 * 1000 }).should('not.exist')
      cy.stepLog({ message: 'the attachment is in progress' })
      cy.location('pathname', { timeout: 30 * 1000 }).should(
        'eq',
        '/rattachement-en-cours'
      )
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

      // Hack because "aller au contenu" is focued by `useFocus`
      cy.findByRole('link', { name: /Aller au contenu/ })
        .focus()
        .click()

      cy.stepLog({ message: 'I chose to join the space' })
      cy.contains('Rejoindre cet espace').click()

      cy.findByTestId('confirm-dialog-button-confirm').click()
      cy.wait('@postOfferers').its('response.statusCode').should('eq', 201)

      cy.findByText('Accéder à votre espace').click()

      cy.location('pathname', { timeout: 30 * 1000 }).should(
        'eq',
        '/rattachement-en-cours'
      )
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
