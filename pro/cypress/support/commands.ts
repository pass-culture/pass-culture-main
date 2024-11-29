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
    Cypress.env('adageToken', response.body.token)
  })
})

// See https://github.com/cypress-io/cypress/issues/1570#issuecomment-891244917
// Workaround bc onChange not triggered for an input type='range' rendered by React
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

// Workaround to format log. See https://github.com/cypress-io/cypress/issues/2134
// and https://github.com/cypress-io/cypress/issues/2134#issuecomment-1692593562

/**
 *  Helper function to convert hex colors to rgb
 * @param {string} hex - hex color
 * @returns {string}
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

/**
 * Print in Cypress UI/Cloud a message with a formatted style
 * @param {string} log.message - The content of the message.
 *
 * @example
 * cy.stepLog({ message: 'I do this' })
 */

Cypress.Commands.add('stepLog', ({ message }) => {
  createCustomLog()
  Cypress.log({
    name: `ptf-STEP`,
    displayName: `STEP`,
    message,
  })
})

export {}
