import { MailSlurp } from 'mailslurp-client'

declare namespace Cypress {
  interface Chainable {
    login(params: {
      email: string
      password: string
      redirectUrl?: string
      refusePopupCookies?: boolean
    }): Chainable

    mailslurp: () => Promise<MailSlurp>

    setFeatureFlags(features: Feature[]): Chainable

    refuseCookies(): Chainable

    getFakeAdageToken(): Chainable

    setSliderValue(value: number): Chainable
  }
}

interface Feature {
  name: string
  isActive: boolean
}
