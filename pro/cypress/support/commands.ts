/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

import '@testing-library/cypress/add-commands'

Cypress.on('uncaught:exception', () => {
  // returning false here prevents Cypress from failing the test
  return false
})

// eslint-disable-next-line no-undef
Cypress.Commands.add('setFeatureFlags', (features: Feature[]) => {
  cy.request({
    method: 'PATCH',
    url: 'http://localhost:5001/testing/features',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      features,
    }),
  }).then((response) => {
    expect(response.status).to.equal(204)
  })
})

Cypress.Commands.add('getFakeAdageToken', () => {
  cy.request({
    method: 'GET',
    url: 'http://localhost:5001/adage-iframe/testing/token',
  }).then((response) => {
    return cy.wrap(response.body.token)
  })
})

Cypress.Commands.add(
  'setSliderValue',
  { prevSubject: 'element' },
  (subject, value) => {
    const element = subject[0]

    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype,
      'value'
    )?.set

    nativeInputValueSetter?.call(element, value)
    element.dispatchEvent(new Event('input', { bubbles: true }))
  }
)

export function createCustomLogStyles(name: string, hexColor: string) {
  const topDocumentHead = window.top?.document.head
  if (
    !topDocumentHead ||
    topDocumentHead.querySelector(
      `style[data-cy-custom-command-styles="custom-log-styles-${name}"]`
    )
  ) {
    return
  }
  const logStyle = document.createElement('style')

  logStyle.setAttribute(
    'data-cy-custom-command-styles',
    `custom-log-styles-${name}`
  )

  logStyle.textContent = `
  .command.command-name-${name} {
    .command-method {
      margin-right: 0.5rem;
      border-radius: 0.125rem;
      border: 1px solid ${hexColor};
      padding: 0.125rem 0.375rem;
      text-transform: uppercase;
      background-color: ${hexColor}30;
    }

    .command-message,
    .command-method {
      color: ${hexColor} !important;
    }
  }`

  Cypress.$(topDocumentHead).append(logStyle)
}

Cypress.Commands.add('stepLog', ({ message }) => {
  createCustomLogStyles('STEP', '#fbbf24') //  Yellow
  Cypress.log({
    name: `STEP`,
    message,
  })
})

Cypress.Commands.add('a11yLog', (violations) => {
  createCustomLogStyles('A11Y', '#ffa079') //  Orange

  violations.map((violation) => {
    Cypress.log({
      name: `A11Y`,
      message: violation.description,
      consoleProps: () => violation,
    })
  })
})

Cypress.Commands.add(
  'sandboxCall',
  (
    method: 'GET' | 'POST',
    url: string,
    onRequest: (response: any) => void,
    retry: boolean = true
  ) => {
    cy.request({
      method,
      url,
      retryOnNetworkFailure: true,
      failOnStatusCode: false,
      timeout: 1000 * 120, // With test parralelization, the api could be slower, so, we'll wait a little.
    }).then((response) => {
      if (response.status === 200) {
        onRequest(response)
      } else if (retry) {
        Cypress.log({
          name: 'sandboxCall-error',
          displayName: `Sandbox call error`,
          message: JSON.stringify(response),
        })
        // We try to wait before doing the call again
        // eslint-disable-next-line cypress/no-unnecessary-waiting
        cy.wait(4000)
        cy.sandboxCall(method, url, onRequest, false)
      }
    })
  }
)

Cypress.Commands.add(
  'clickWithRetryIfStillVisible',
  { prevSubject: true },
  (subject: JQuery) => {
    // eslint-disable-next-line cypress/no-assigning-return-values
    const element = cy.wrap(subject)
    element.click().then(($el) => {
      if (Cypress.dom.isAttached($el)) {
        // eslint-disable-next-line no-console
        console.log('element still visible, retrying click')
        element.click()
      }
    })
  }
)
