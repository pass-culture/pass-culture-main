import * as yup from 'yup'

import { getNthParentFormValues } from '@/commons/utils/yupValidationTestHelpers'

describe('getNthParentFormValues', () => {
  it('should return the correct parent', () => {
    const context = {
      from: [
        { value: { child: 0 } },
        { value: { parent1: 1 } },
        { value: { parent2: 2 } },
      ],
    }

    expect(
      getNthParentFormValues(context as unknown as yup.TestContext<unknown>, 1)
    ).toEqual({ parent1: 1 })
  })

  it('should throw errors if context is invalid', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const context = {
      from: [
        { child: 0 },
        { value: { parent1: 1 } },
        { value: { parent2: 2 } },
      ],
    }

    expect(() =>
      getNthParentFormValues(context as unknown as yup.TestContext<unknown>, 1)
    ).toThrowError('Missing or invalid "from" attribute in `testContext`.')
  })

  it('should throw error if parent is invalid', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const context = {
      from: [
        { value: { child: 0 } },
        { value: { parent1: 1 } },
        { value: { parent2: 2 } },
      ],
    }

    expect(() =>
      getNthParentFormValues(context as unknown as yup.TestContext<unknown>, 10)
    ).toThrowError(
      "Parent depth (10) can't be greater than the number of available parents (3)."
    )
  })
})
