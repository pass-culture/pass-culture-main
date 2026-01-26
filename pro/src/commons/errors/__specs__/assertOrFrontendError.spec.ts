import type { Mock } from 'vitest'

import { assertOrFrontendError } from '../assertOrFrontendError'
import { FrontendError } from '../FrontendError'
import { handleUnexpectedError } from '../handleUnexpectedError'

vitest.mock('../handleUnexpectedError', () => ({
  handleUnexpectedError: vitest.fn(),
}))

const mockedHandleUnexpectedError = handleUnexpectedError as Mock

describe('assertOrFrontendError', () => {
  beforeEach(() => {
    mockedHandleUnexpectedError.mockClear()
  })

  // This test is a placeholder to check that TS type-checking correctly infers types after a call to `assertOrFrontendError()`.
  // If it was not, this code couldn't compile.
  it('should respect TypeScript type-checking', () => {
    /* eslint-disable @typescript-eslint/no-unused-vars */

    const items = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
    ]

    const foundItem = items.find((item) => item.id === 1)
    // @ts-expect-error `'foundItem' is possibly 'undefined'.`
    const _impossibleExtraction = foundItem.id
    assertOrFrontendError(foundItem, 'This should not fail')
    // @ts-expect-no-error
    const _extraction = foundItem.id

    const mixedArray = [1, 'two', true]
    const firstMixedArrayItem = mixedArray[0]
    // @ts-expect-error `The left-hand side of an arithmetic operation must be of type 'any', 'number', 'bigint' or an enum type.`
    const _impossibleCalculation = firstMixedArrayItem / 2
    assertOrFrontendError(
      typeof firstMixedArrayItem === 'number',
      'This should not fail'
    )
    // @ts-expect-no-error
    const _calculation = firstMixedArrayItem / 2

    expect(handleUnexpectedError).toHaveBeenCalledTimes(0)

    /* eslint-enable @typescript-eslint/no-unused-vars */
  })

  it('should NOT call handleUnexpectedError() when condition is truthy', () => {
    expect(() =>
      assertOrFrontendError(true, 'This should not fail')
    ).not.toThrow()
    expect(() =>
      assertOrFrontendError({}, 'This should not fail')
    ).not.toThrow()
    expect(() =>
      assertOrFrontendError([], 'This should not fail')
    ).not.toThrow()

    expect(() =>
      assertOrFrontendError('abc', 'This should not fail')
    ).not.toThrow()
    expect(() =>
      assertOrFrontendError(123, 'This should not fail')
    ).not.toThrow()

    expect(handleUnexpectedError).toHaveBeenCalledTimes(0)
  })

  it('should call handleUnexpectedError() when condition is falsy', () => {
    expect(() => assertOrFrontendError(false, 'This should fail')).toThrow()
    expect(() => assertOrFrontendError(null, 'This should fail')).toThrow()
    expect(() => assertOrFrontendError(undefined, 'This should fail')).toThrow()

    expect(() => assertOrFrontendError(0, 'This should not fail')).toThrow()
    expect(() => assertOrFrontendError('', 'This should not fail')).toThrow()

    expect(handleUnexpectedError).toHaveBeenCalledTimes(5)
  })

  it('should call handleUnexpectedError() and throw an error', () => {
    const condition = false
    const errorInternalMessage = 'The condition was not met'

    const call = () => assertOrFrontendError(condition, errorInternalMessage)

    expect(call).toThrow(FrontendError)
    expect(call).toThrow(errorInternalMessage)

    expect(handleUnexpectedError).toHaveBeenCalledTimes(2)

    const firstCallArgs = mockedHandleUnexpectedError.mock.calls[0]
    const errorInstance = firstCallArgs[0]

    expect(errorInstance.message).toBe(errorInternalMessage)
  })
})
