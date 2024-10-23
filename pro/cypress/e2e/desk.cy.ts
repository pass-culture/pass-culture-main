import { addDays, format } from 'date-fns'

import { logAndGoToPage } from '../support/helpers.ts'

describe('Desk (Guichet) feature', () => {
  let login: string

  beforeEach(() => {
    cy.visit('/connexion')
    cy.request({
      method: 'GET',
      url: 'http://localhost:5001/sandboxes/pro/create_pro_user_with_bookings',
    }).then((response) => {
      login = response.body.user.email
    })
  })

  it('I should see help information on desk page', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'The identity check message is displayed' })
    cy.findByText(
      'N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque.'
    )
    cy.findByText(
      'Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.'
    )

    cy.stepLog({
      message: 'I can click and open the "Modalités de retrait et CGU" page',
    })
    cy.findByText('Modalités de retrait et CGU')
      .invoke('removeAttr', 'target')
      .click() // remove target to not open it in a new tab (not supported by cypress)
    cy.origin('https://aide.passculture.app/', () => {
      cy.url().should(
        'include',
        'Acteurs-Culturels-Modalit%C3%A9s-de-retrait-et-CGU'
      )
    })
  })

  it('Should validate a countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "2XTM3W"' })
    cy.findByLabelText('Contremarque').type('2XTM3W')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Coupon vérifié, cliquez sur "Valider" pour enregistrer')
    cy.findByText('Valider la contremarque').click()

    cy.stepLog({ message: 'the booking is done' })
    cy.findByText('Contremarque validée !')
  })

  it('It should decline a non-valid countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "XXXXXX"' })
    cy.findByLabelText('Contremarque').type('XXXXXX')

    cy.stepLog({ message: 'the countermark is rejected as invalid' })
    cy.findByTestId('desk-message').should(
      'have.text',
      "La contremarque n'existe pas"
    )
    cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it('It should decline an event countermark more than 48h before', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "TOSOON"' })
    cy.findByLabelText('Contremarque').type('TOSOON')

    cy.stepLog({ message: 'the countermark is rejected as invalid' })
    const date = format(addDays(new Date(), 2), 'dd/MM/yyyy')
    cy.findByTestId('desk-message')
      .should(
        'contain.text',
        `Vous pourrez valider cette contremarque à partir du ${date}`
      )
      .and('contain.text', `une fois le délai d’annulation passé.`)
    cy.findByText('Valider la contremarque').should('be.disabled')
  })

  it('Should invalidate a already used countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "XUSEDX"' })
    cy.findByLabelText('Contremarque').type('XUSEDX')
    cy.findByText(/Cette contremarque a été validée./)

    cy.stepLog({ message: 'I invalidate the countermark' })
    cy.findByText('Invalider la contremarque').click()
    cy.findByText('Continuer').click()

    cy.stepLog({ message: 'The countermark is invalidated' })
    cy.findByText('Contremarque invalidée !')
  })

  it('Should not be able to validate an other pro countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "OTHERX"' })
    cy.findByLabelText('Contremarque').type('OTHERX')

    cy.stepLog({ message: 'I cannot validate the countermark' })
    cy.findByText('Valider la contremarque').should('be.disabled')
    cy.findByText(
      "Vous n'avez pas les droits nécessaires pour voir cette contremarque"
    )
  })

  it('Should not be able to validate a cancelled countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "CANCEL"' })
    cy.findByLabelText('Contremarque').type('CANCEL')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').should('be.disabled')
    cy.findByText('Cette réservation a été annulée')
  })

  it('Should not be able to validate a reimbursed countermark', () => {
    logAndGoToPage(login, '/guichet')

    cy.stepLog({ message: 'I add this countermark "REIMBU"' })
    cy.findByLabelText('Contremarque').type('REIMBU')

    cy.stepLog({ message: 'I validate the countermark' })
    cy.findByText('Valider la contremarque').should('be.disabled')
    cy.findByText('Cette réservation a été remboursée')
  })
})
