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

/**
 *  Helper function to convert hex colors to rgb
 *  Workaround to format log
 * @param {string} hex - hex color
 * @returns {string}
 * @see https://github.com/cypress-io/cypress/issues/2134
 * @see https://github.com/cypress-io/cypress/issues/2134#issuecomment-1692593562
 *
 * @example
 * // returns "255 255 255"
 * hex2rgb("#ffffff")
 */
function hex2rgb(hex: string): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)

  return `${r} ${g} ${b}`
}

const yellow = '#fbbf24' // Yellow
export function createCustomLog() {
  const logStyle = document.createElement('style')

  logStyle.textContent = `
        .command.command-name-ptf-STEP span.command-method {
            margin-right: 0.5rem;
            min-width: 10px;
            border-radius: 0.125rem;
            border-width: 1px;
            padding-left: 0.375rem;
            padding-right: 0.375rem;
            padding-top: 0.125rem;
            padding-bottom: 0.125rem;
            text-transform: uppercase;

            border-color: rgb(${hex2rgb(yellow)} / 1);
            background-color: rgb(${hex2rgb(yellow)} / 0.2);
            color: rgb(${hex2rgb(yellow)} / 1) !important;
        }

        .command.command-name-ptf-STEP span.command-message{
            color: rgb(${hex2rgb(yellow)} / 1);
            font-weight: normal;
        }

        .command.command-name-ptf-STEP span.command-message strong,
        .command.command-name-ptf-STEP span.command-message em { 
            color: rgb(${hex2rgb(yellow)} / 1);
        }
    ` // @ts-expect-error: Object is possibly 'null'.
  Cypress.$(window.top.document.head).append(logStyle)
}

Cypress.Commands.add('stepLog', ({ message }) => {
  createCustomLog()
  Cypress.log({
    name: `ptf-STEP`,
    displayName: `STEP`,
    message,
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
        cy.wait(4000)
        cy.sandboxCall(method, url, onRequest, false)
      }
    })
  }
)

export {}
