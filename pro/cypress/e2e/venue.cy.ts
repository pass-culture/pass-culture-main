import {
  MOCKED_BACK_ADDRESS_LABEL,
  MOCKED_BACK_ADDRESS_STREET,
} from '../support/constants.ts'
import { interceptSearch5Adresses, sessionLogInAndGoToPage } from '../support/helpers.ts'

describe('Create and update venue', () => {
  let login: string
  let siret: string
  let siren: string

  before(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      login = response.body.user.email
      siren = response.body.siren
    })
  })

  beforeEach(() => {
    cy.intercept({ method: 'PATCH', url: '/venues/*' }).as('patchVenue')
    cy.intercept(
      'GET',
      'https://api-adresse.data.gouv.fr/search/?limit=1&q=*',
      (req) =>
        req.reply({
          statusCode: 200,
          body: addressInterceptionPayload,
        })
    ).as('searchAddress1')
    interceptSearch5Adresses()
    cy.intercept({ method: 'POST', url: '/venues' }).as('postVenues')
  })

  it('As a pro user, I should be able to add a venue without SIRET', () => {
    const venueNameWithoutSiret = 'Lieu sans Siret'
    sessionLogInAndGoToPage('Session venue', login, '/accueil')

    cy.stepLog({ message: 'I want to add a venue' })
    cy.findByText('Ajouter un lieu', { timeout: 60 * 1000 }).click()

    cy.stepLog({ message: 'I choose a venue which already has a Siret' })
    cy.findByText('Ce lieu possède un SIRET').click()

    cy.stepLog({ message: 'I add venue without Siret details' })
    cy.findByLabelText('Commentaire du lieu sans SIRET *').type(
      'Commentaire du lieu sans SIRET'
    )
    cy.findByLabelText('Raison sociale *').type(venueNameWithoutSiret)
    cy.findByLabelText('Adresse postale *')

    cy.findByLabelText('Adresse postale *').type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    cy.findByLabelText('Activité principale *').select('Centre culturel')
    cy.findByText('Visuel').click()
    cy.findByLabelText('Adresse email *').type('email@example.com')

    cy.stepLog({ message: 'I validate venue step' })
    cy.findByText('Enregistrer et créer le lieu').click()
    cy.wait('@postVenues', { timeout: 60 * 1000 })
      .its('response.statusCode')
      .should('eq', 201)

    cy.stepLog({ message: 'I skip offer creation' })
    cy.findByText('Plus tard').click()
    cy.url().should('contain', 'accueil')

    cy.stepLog({ message: 'I open my venue without Siret resume' })
    cy.findByRole('link', {
      name: 'Gérer la page de ' + venueNameWithoutSiret,
    }).click()
    cy.url().should('contain', 'structures').and('contain', 'lieux')
    cy.findAllByTestId('spinner').should('not.exist')
    cy.contains(venueNameWithoutSiret).should('be.visible')

    cy.stepLog({ message: 'I add an image to my venue' })
    cy.findByText('Ajouter une image').click()
    cy.get('input[type=file]').selectFile('cypress/data/dog.jpg', {
      force: true,
    })
    // eslint-disable-next-line cypress/no-unnecessary-waiting
    cy.wait(1000) // todo: pas réussi à attendre l'image chargée
    cy.contains(
      'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci'
    )
    cy.findByText('Suivant').click()
    cy.contains(
      'Prévisualisation de votre image dans l’application pass Culture'
    )
    cy.findByText('Enregistrer').click()

    cy.stepLog({ message: 'I should see a success message' })
    cy.findByTestId('global-notification-success', {
      timeout: 30 * 1000,
    }).should('contain', 'Vos modifications ont bien été prises en compte')

    cy.stepLog({ message: 'I should see details of my venue' })
    cy.contains(venueNameWithoutSiret)
    cy.findByText('Modifier l’image').should('be.visible')
  })

  it('As a pro user, I should be able to add a venue with SIRET', () => {
    const venueNameWithSiret = 'Lieu avec Siret'
    siret = siren + '12345'

    cy.intercept('GET', `/sirene/siret/${siret}`, (req) =>
      req.reply({
        statusCode: 200,
        body: {
          siret: siret,
          name: 'Ministère de la Culture',
          active: true,
          address: {
            street: MOCKED_BACK_ADDRESS_STREET,
            postalCode: '75001',
            city: 'Paris',
          },
          ape_code: '90.03A',
          legal_category_code: '1000',
        },
      })
    ).as('getSiretVenue')

    sessionLogInAndGoToPage('Session venue', login, '/accueil')

    cy.stepLog({ message: 'I want to add a venue' })
    cy.findByText('Ajouter un lieu', { timeout: 60 * 1000 }).click()

    cy.stepLog({ message: 'I add a valid Siret' })
    cy.findByLabelText('SIRET du lieu *').type(siret + '{enter}')
    cy.wait(['@getSiretVenue', '@searchAddress1'])
    cy.findByTestId('error-siret').should('not.exist')

    cy.stepLog({ message: 'I add venue with Siret details' })
    cy.findByLabelText('Nom public').type(venueNameWithSiret)
    cy.findByLabelText('Activité principale *').select('Festival')
    cy.findByText('Moteur').click()
    cy.findByText('Auditif').click()
    cy.findByLabelText('Adresse email *').type('email@example.com')

    cy.stepLog({ message: 'I validate venue step' })
    cy.findByText('Enregistrer et créer le lieu').click()
    cy.wait('@postVenues', { timeout: 60 * 1000 })
      .its('response.statusCode')
      .should('eq', 201)

    cy.stepLog({ message: 'I skip offer creation' })
    cy.findByText('Plus tard').click()
    cy.url().should('contain', 'accueil')

    cy.stepLog({ message: 'I should see my venue with Siret resume' })
    cy.reload() // newly created venue sometimes not displayed
    cy.findByRole('link', {
      name: 'Gérer la page de ' + venueNameWithSiret + '',
    }).click()
    cy.contains(venueNameWithSiret).should('be.visible')
  })

  it('As a pro user, I should be able to update a venue', () => {
    const textRetrait = 'En main bien propres'
    const textDesc = 'On peut ajouter des choses'
    sessionLogInAndGoToPage('Session venue', login, '/accueil')

    cy.stepLog({ message: 'I go to the venue page in Individual section' })
    cy.findByText('Votre page partenaire', {
      timeout: 60 * 1000,
    }).scrollIntoView()
    cy.findByText('Votre page partenaire').should('be.visible')
    cy.findByText('Vos adresses').scrollIntoView()
    cy.findByText('Vos adresses').should('be.visible')
    cy.findByText('Gérer votre page pour le grand public').click()
    cy.findByText('À propos de votre activité').should('be.visible')
    cy.findByText('Modifier').click()

    cy.stepLog({ message: 'I update Individual section data' })
    cy.findAllByLabelText('Description').type('{selectall}{del}' + textDesc)
    cy.findByText('Non accessible').click()
    cy.findByText('Psychique ou cognitif').click()
    cy.findByText('Auditif').click()
    cy.findByText('Enregistrer').click()
    cy.wait('@patchVenue')

    cy.stepLog({ message: 'Individual section data should be updated' })
    cy.url().should('include', '/structures').and('include', '/lieux')
    cy.findByText('Vos informations pour le grand public').should('be.visible')
    cy.findByText(textDesc).should('be.visible')

    cy.stepLog({ message: 'I go to the venue page in Paramètres généraux' })
    cy.findAllByTestId('spinner').should('not.exist')
    cy.findByText('Paramètres généraux').click()
    cy.url()
      .should('include', '/structures')
      .and('include', '/lieux')
      .and('include', '/parametres')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I update Paramètres généraux data' })
    cy.findByLabelText(
      'Label du ministère de la Culture ou du Centre national du cinéma et de l’image animée'
    ).select('Musée de France')
    cy.findByLabelText('Informations de retrait').type(
      '{selectall}{del}' + textRetrait
    )
    cy.findByText('Enregistrer').click()
    cy.wait('@patchVenue')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'I go to the venue page in Paramètres généraux' })
    cy.url().should('not.include', '/parametres')
    cy.findByText('Paramètres généraux').click()
    cy.url().should('include', '/parametres')
    cy.findAllByTestId('spinner').should('not.exist')

    cy.stepLog({ message: 'paramètres généraux data should be updated' })
    cy.findByText(textRetrait).scrollIntoView()
    cy.findByText(textRetrait).should('be.visible')

    cy.findByTestId('wrapper-venueLabel').within(() => {
      cy.get('select')
        .invoke('val')
        .then((identifiant) => {
          cy.get('option[value="' + identifiant + '"]').should(
            'have.text',
            'Musée de France'
          )
        })
    })
  })
})

const addressInterceptionPayload = {
  type: 'FeatureCollection',
  version: 'draft',
  features: [
    {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [2.337933, 48.863666] },
      properties: {
        label: MOCKED_BACK_ADDRESS_LABEL,
        score: 0.8136893939393939,
        housenumber: '3',
        id: '75101_9575_00003',
        name: MOCKED_BACK_ADDRESS_STREET,
        postcode: '75001',
        citycode: '75101',
        x: 651428.82,
        y: 6862829.62,
        city: 'Paris',
        district: 'Paris 1er Arrondissement',
        context: '75, Paris, Île-de-France',
        type: 'housenumber',
        importance: 0.6169,
        street: 'Rue de Valois',
      },
    },
  ],
  attribution: 'BAN',
  licence: 'ETALAB-2.0',
  query: MOCKED_BACK_ADDRESS_LABEL,
  limit: 1,
}
