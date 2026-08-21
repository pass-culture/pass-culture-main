import { withCallSites } from '../callSite'

describe('withCallSites', () => {
  it('should forward the resolved value of an operation', async () => {
    const sdk = withCallSites({
      getOffer: () => Promise.resolve({ id: 1 }),
    })

    await expect(sdk.getOffer()).resolves.toStrictEqual({ id: 1 })
  })

  it('should forward the arguments of an operation', async () => {
    const getOffer = vi.fn((options: { id: number }) =>
      Promise.resolve(options)
    )
    const sdk = withCallSites({ getOffer })

    await sdk.getOffer({ id: 42 })

    expect(getOffer).toHaveBeenCalledWith({ id: 42 })
  })

  it('should replace the error own frames with those of the caller', async () => {
    const sdk = withCallSites({
      getOffer: async () => {
        // Stands for the generated client: the error is built several awaits
        // away from the caller, so its own stack does not mention it.
        await Promise.resolve()

        const apiError = new Error('500 GET /offers/{id}')
        apiError.name = 'ApiError'
        apiError.stack =
          'ApiError: 500 GET /offers/{id}\n    at request (client.gen.ts:141:25)'

        throw apiError
      },
    })

    const theCallingComponent = async () => {
      try {
        await sdk.getOffer()

        return null
      } catch (error) {
        return error as Error
      }
    }

    const error = await theCallingComponent()

    expect(error?.stack).not.toContain('client.gen.ts')
    expect(error?.stack).toContain('theCallingComponent')
  })

  it('should keep the header line consistent with the error it rethrows', async () => {
    const apiError = new Error('500 GET /offers/{id}')
    apiError.name = 'ApiError'

    const sdk = withCallSites({
      getOffer: () => Promise.reject(apiError),
    })

    const error = await sdk.getOffer().catch((rejected: Error) => rejected)

    expect(error.stack).toMatch(/^ApiError: 500 GET \/offers\/\{id\}/)
  })

  it('should rethrow values that are not errors untouched', async () => {
    const sdk = withCallSites({
      getOffer: () => Promise.reject('not an error'),
    })

    await expect(sdk.getOffer()).rejects.toBe('not an error')
  })

  it('should copy the properties that are not operations as-is', () => {
    const sdk = withCallSites({
      getOffer: () => Promise.resolve(null),
      SOME_CONSTANT: 'unchanged',
    })

    expect(sdk.SOME_CONSTANT).toBe('unchanged')
  })
})
