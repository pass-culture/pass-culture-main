import { getNthParentFormValues } from 'commons/utils/yupValidationTestHelpers'
import * as yup from 'yup'

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
    const context = {
      from: [
        { child: 0 },
        { value: { parent1: 1 } },
        { value: { parent2: 2 } },
      ],
    }

    expect(() =>
      getNthParentFormValues(context as unknown as yup.TestContext<unknown>, 1)
    ).toThrowError('TestContext is not valid')
  })

  it('should throw error if parent is invalid', () => {
    const context = {
      from: [
        { value: { child: 0 } },
        { value: { parent1: 1 } },
        { value: { parent2: 2 } },
      ],
    }

    expect(() =>
      getNthParentFormValues(context as unknown as yup.TestContext<unknown>, 10)
    ).toThrowError('Parent depth is not valid')
  })
})
