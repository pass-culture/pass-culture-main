export class FrontendError extends Error {
  public readonly name = 'FrontendError'

  constructor(internalMessage: string) {
    super(internalMessage)
  }
}
