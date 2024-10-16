declare namespace Cypress {
  interface Chainable {
    login(params: {
      email: string
      password: string
      redirectUrl?: string
      refusePopupCookies?: boolean
    }): Chainable

    setFeatureFlags(features: Feature[]): Chainable

    refuseCookies(): Chainable

    getFakeAdageToken(): Chainable

    setSliderValue(value: number): Chainable<void>

    stepLog(params: { message: string }): Chainable
  }
}

interface Feature {
  name: string
  isActive: boolean
}
