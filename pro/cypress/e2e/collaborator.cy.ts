import { logInAndGoToPage } from '../support/helpers.ts'

describe('Collaborator list feature', () => {
  let login: string
  let randomEmail: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_regular_pro_user',
    }).then((response) => {
      login = response.body.user.email
    })

    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/clear_email_list',
    }).then((response) => {
      expect(response.status).to.eq(200)
    })
    randomEmail = `collaborator${Math.random()}@example.com`
  })

  it('I can add a new collaborator and he receives an email invitation', () => {
    logInAndGoToPage(login, '/accueil')

    cy.stepLog({ message: 'I close the collective budget information modal' })
    cy.findAllByText('Fermer').click()

    cy.stepLog({ message: 'open collaborator page' })
    cy.findAllByText('Collaborateurs').click()

    cy.stepLog({ message: 'wait for collaborator page display' })
    cy.url().should('include', '/collaborateurs')
    cy.findAllByTestId('spinner').should('not.exist')
    cy.contains(login)

    cy.stepLog({ message: 'add a collaborator in the list' })
    cy.findByText('Ajouter un collaborateur').click()
    cy.findByLabelText('Adresse email *').type(randomEmail)
    cy.findByText('Inviter').click()

    cy.stepLog({ message: 'check notification about invitation sent' })
    cy.findAllByTestId('global-notification-success').should(
      'contain',
      `L'invitation a bien été envoyée.`
    )

    cy.stepLog({
      message: 'check login validated and new collaborator waiting status',
    })
    cy.findAllByTestId('spinner').should('not.exist')
    cy.contains(randomEmail).next().should('have.text', 'En attente')
    cy.contains(login).next().should('have.text', 'Validé')

    cy.stepLog({ message: 'check email received' })
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/get_unique_email',
      timeout: 60000,
    }).then((response) => {
      expect(response.status).to.eq(200)
      expect(response.body.To).to.eq(randomEmail)
      expect(response.body.params.OFFERER_NAME).to.contain(
        'Le Petit Rintintin Management'
      )
    })
  })
})
