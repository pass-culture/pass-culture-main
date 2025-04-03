import { MOCKED_BACK_ADDRESS_LABEL } from '../support/constants.ts'
import {
  interceptSearch5Adresses,
  sessionLogInAndGoToPage,
} from '../support/helpers.ts'

describe('Create individual offers with OA', () => {
  let login: string

  before(() => {
    cy.wrap(Cypress.session.clearAllSavedSessions())
    cy.visit('/connexion')
    cy.sandboxCall(
      'GET',
      'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
      (response) => {
        login = response.body.user.email
      }
    )
  })

  beforeEach(() => {
    sessionLogInAndGoToPage(
      'Session OA Individual offer',
      login,
      '/offre/creation'
    )
    cy.intercept({ method: 'GET', url: '/offers/*' }).as('getOffer')
    cy.intercept({ method: 'POST', url: '/offers/draft' }).as('postOffersDraft')
    cy.intercept({ method: 'PATCH', url: '/offers/*' }).as('patchOffer')
    cy.intercept({ method: 'GET', url: '/offers/*/stocks/*' }).as('getStocks')
    cy.intercept({ method: 'POST', url: '/stocks/bulk' }).as('postStocks')
    cy.intercept({ method: 'PATCH', url: '/offers/publish' }).as('publishOffer')
    cy.intercept({ method: 'GET', url: '/offers/categories' }).as(
      'getCategories'
    )
    cy.intercept({ method: 'GET', url: '/venues?offererId=*' }).as(
      'getVenuesForOfferer'
    )
    interceptSearch5Adresses()
    cy.contains('À qui destinez-vous cette offre ?')
  })

  it('I should be able to create an individual offer (event)', () => {
    const eventName = 'Offer with OA (event) ' + (Cypress.currentRetry + 1)
    cy.stepLog({
      message: 'I want to create "Un évènement physique daté" offer',
    })
    cy.findByText('Au grand public').click()
    cy.findByText('Un évènement physique daté').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill in event details' })
    cy.findByLabelText('Titre de l’offre *').type(eventName)
    cy.findByLabelText('Description').type(
      'Une PO invite des développeurs à dîner...'
    )
    cy.findByLabelText('Catégorie *').select('Spectacle vivant')
    cy.findByLabelText('Sous-catégorie *').select('Spectacle, représentation')
    cy.findByLabelText('Type de spectacle *').select('Théâtre')
    cy.findByLabelText('Sous-type *').select('Comédie')

    cy.stepLog({ message: 'I validate event details step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@postOffersDraft'])

    cy.stepLog({ message: 'I fill in event useful informations' })
    cy.findByText('Retrait sur place (guichet, comptoir...)').click()
    cy.findByLabelText('Email de contact *').type('passculture@example.com')

    cy.stepLog({ message: 'I validate event useful informations step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer'])

    cy.stepLog({ message: 'I fill in prices' })
    cy.findByLabelText('Intitulé du tarif').should('have.value', 'Tarif unique')

    cy.findByLabelText('Prix par personne').type('100')

    cy.stepLog({ message: 'I validate prices step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@getOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 3,
    })

    const fromDate = new Date()
    fromDate.setDate(fromDate.getDate() + 2)
    const fromDateStr = fromDate.toISOString().split('T')[0]
    const toDate = new Date()
    toDate.setDate(toDate.getDate() + 12)
    const toDateStr = toDate.toISOString().split('T')[0]
    cy.stepLog({ message: 'I fill in recurrence' })
    cy.findByText('Ajouter une ou plusieurs dates').click()
    cy.findByText('Tous les jours').click()
    cy.findByLabelText('Du *').type(fromDateStr)
    cy.findByLabelText('Au *').type(toDateStr)
    cy.findByLabelText('Horaire 1 *').type('18:30')
    cy.findByLabelText('Tarif *').select('100,00\xa0€ - Tarif unique')

    cy.stepLog({ message: 'I validate recurrence step' })
    cy.findByText('Valider').click()
    cy.wait(['@postStocks'])

    cy.findByText('Enregistrer et continuer').click()
    cy.contains('Accepter les réservations "Duo" : Oui')

    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()
    cy.findByText('Plus tard').click()
    cy.wait('@publishOffer', {
      timeout: 60000,
      requestTimeout: 60000,
      responseTimeout: 60000,
    })
    cy.wait('@getOffer', { timeout: 60000 })

    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 2,
      responseTimeout: 60 * 1000 * 2,
    })

    cy.stepLog({ message: 'my new offer should be displayed' })
    cy.url().should('contain', '/offres')
    cy.contains(eventName)
    cy.contains('11 dates')

    cy.stepLog({ message: 'I want to update my offer' })
    cy.findByText(eventName).click()
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')
    cy.contains('Adresse : 1 boulevard Poissonnière 75002 Paris')
    cy.findByText('Modifier').click()
    cy.url().should('contain', '/edition/pratiques')

    cy.stepLog({ message: 'I update the OA' })
    cy.findByLabelText(
      'Mon Lieu – 1 boulevard Poissonnière 75002 Paris'
    ).should('be.checked')
    cy.findByLabelText('À une autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse'
    )

    cy.findByLabelText('Adresse postale *').type(MOCKED_BACK_ADDRESS_LABEL)
    cy.wait('@search5Address').its('response.statusCode').should('eq', 200)
    cy.findByTestId('list').contains(MOCKED_BACK_ADDRESS_LABEL).click()
    cy.findByText('Enregistrer les modifications').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })
    cy.contains('Intitulé : Libellé de mon adresse')
    cy.contains(`Adresse : ${MOCKED_BACK_ADDRESS_LABEL}`)
  })

  it('I should be able to create an individual offer (thing)', () => {
    const offerTitle = 'Offer with OA (thing) ' + (Cypress.currentRetry + 1)
    const offerDesc =
      'Une quête pour obtenir la question ultime sur la vie, l’univers et tout le reste.'

    cy.stepLog({ message: 'I want to create "Un bien physique" offer' })
    cy.findByText('Au grand public').click()
    cy.findByText('Un bien physique').click()
    cy.findByText('Étape suivante').click()

    cy.stepLog({ message: 'I fill in details for physical offer' })
    cy.findByLabelText('Titre de l’offre *').type(offerTitle)
    cy.findByLabelText('Description').type(offerDesc)

    // Random 13-digit number because we can't use the same EAN twice
    const ean = String(
      Math.floor(1000000000000 + Math.random() * 9000000000000)
    )
    cy.wrap(ean).as('ean')
    cy.findByLabelText('Catégorie *').select('Livre')
    cy.findByLabelText('Sous-catégorie *').select('Livre papier')
    cy.findByLabelText('Auteur').type('Douglas Adams')
    cy.findByLabelText('EAN-13 (European Article Numbering)').type(ean)
    cy.findByText('Ajouter une image').click()
    cy.get('input[type=file]').selectFile('cypress/data/librairie.jpeg', {
      force: true,
    })
    cy.findByLabelText('Crédit de l’image').type(
      'Les êtres les plus intelligents de l’univers'
    )
    cy.get('input[type=range]').setSliderValue(1.7)

    cy.findByText('Enregistrer').click()

    cy.stepLog({ message: 'the details of offer should be correct' })
    cy.findByLabelText('Titre de l’offre *').should('have.value', offerTitle)
    cy.findByLabelText('Description').should('have.text', offerDesc)

    // With a 1.7x zoom, width=470 and height=705
    cy.findAllByTestId('image-preview').then(($img) => {
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalWidth')
        .and('eq', 470)
      cy.wrap($img)
        .should('be.visible')
        .should('have.prop', 'naturalHeight')
        .and('eq', 705)
    })

    cy.stepLog({ message: 'I validate offer details step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@postOffersDraft'])

    cy.stepLog({ message: 'I fill in useful informations for physical offer' })
    cy.findByLabelText('Informations de retrait').type(
      'Seuls les dauphins et les souris peuvent le lire.'
    )
    cy.findByText('Non accessible').click()
    cy.findByText('Psychique ou cognitif').click()
    cy.findByText('Moteur').click()
    cy.findByText('Auditif').click()

    cy.findByText('Être notifié par email des réservations').click()

    cy.stepLog({ message: 'I validate offer useful informations step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@getOffer', '@patchOffer', '@getStocks'], {
      responseTimeout: 60 * 1000 * 3,
    })

    cy.stepLog({ message: 'I fill in stocks' })
    cy.get('#price').type('42')
    cy.get('#bookingLimitDatetime').type('2042-05-03')
    cy.get('#quantity').type('42')

    cy.stepLog({ message: 'I validate stocks step' })
    cy.findByText('Enregistrer et continuer').click()
    cy.wait(['@patchOffer', '@postStocks', '@getOffer'], {
      responseTimeout: 30 * 1000,
    })

    cy.stepLog({ message: 'I publish my offer' })
    cy.findByText('Publier l’offre').click()

    cy.stepLog({ message: 'I go to the offers list' })
    cy.findByText('Voir la liste des offres').click()
    cy.url().should('contain', '/offres')
    cy.wait(['@getOffer', '@getCategories'], {
      requestTimeout: 60 * 1000 * 2,
      responseTimeout: 60 * 1000 * 2,
    })

    cy.stepLog({ message: 'my new physical offer should be displayed' })
    cy.contains(offerTitle)
    cy.get('@ean').then((ean) => {
      cy.contains(ean.toString())
    })

    cy.stepLog({ message: 'I want to update my offer' })
    cy.findByText(offerTitle).click()
    cy.findByText('Informations pratiques').click()
    cy.url().should('contain', '/pratiques')
    cy.contains('Adresse : 1 boulevard Poissonnière 75002 Paris')
    cy.findByText('Modifier').click()
    cy.url().should('contain', '/edition/pratiques')

    cy.stepLog({ message: 'I update the OA' })
    cy.findByLabelText(
      'Mon Lieu – 1 boulevard Poissonnière 75002 Paris'
    ).should('be.checked')
    cy.findByLabelText('À une autre adresse').click()
    cy.findByLabelText('Intitulé de la localisation').type(
      'Libellé de mon adresse custom'
    )
    cy.findByText('Vous ne trouvez pas votre adresse ?').click()

    cy.stepLog({ message: 'I want to put a custom address' })
    cy.findAllByLabelText('Adresse postale *').last().type('Place de la gare')
    cy.findAllByLabelText('Code postal *').type('123123')
    cy.findAllByLabelText('Ville *').type('Y')
    // eslint-disable-next-line cypress/unsafe-to-chain-command
    cy.findAllByLabelText('Coordonnées GPS *')
      .type('48.853320, 2.348979')
      .blur()
    cy.findByText('Vérifiez la localisation en cliquant ici').should(
      'be.visible'
    )
    cy.findByText('Enregistrer les modifications').click()
    cy.wait(['@getOffer', '@patchOffer'], {
      responseTimeout: 60 * 1000 * 2,
    })
    cy.contains('Intitulé : Libellé de mon adresse custom')
    cy.contains('Adresse : Place de la gare 12312 Y')
  })
})
