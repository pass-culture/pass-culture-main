declare namespace Cypress {
  interface Chainable {
    setFeatureFlags(features: Feature[]): Chainable

    getFakeAdageToken(): Chainable

    setSliderValue(value: number): Chainable<void>

    stepLog(params: { message: string }): Chainable
  }
}

interface Feature {
  name: string
  isActive: boolean
}
