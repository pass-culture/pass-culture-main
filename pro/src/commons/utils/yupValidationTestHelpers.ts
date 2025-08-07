import * as yup from 'yup'

import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import { hasProperty } from './types'

export const getYupValidationSchemaErrors = async <T extends yup.AnyObject>(
  validationSchema: yup.ObjectSchema<T>,
  testInput: any
): Promise<string[]> => {
  try {
    await validationSchema.validate(testInput, { abortEarly: false })
  } catch (error) {
    /* istanbul ignore next this condition should never been evaluated to false */
    if (error instanceof yup.ValidationError) {
      return error.errors
    }
  }

  return []
}

const hasValidFromAttribute = (
  element: unknown
): element is { from: { value: unknown }[] } =>
  hasProperty(element, 'from') &&
  Array.isArray(element.from) &&
  element.from.every((values) => hasProperty(values, 'value'))

// With TestContext, current field parents can be accessed,
// each index of the "from" array corresponds to a parent field one level higher
export const getNthParentFormValues = (
  testContext: yup.TestContext<unknown>,
  parentDepth: number
): unknown => {
  assertOrFrontendError(
    hasValidFromAttribute(testContext),
    'Missing or invalid "from" attribute in `testContext`.'
  )
  const allParentValues = testContext.from
  assertOrFrontendError(
    parentDepth <= allParentValues.length,
    `Parent depth (${parentDepth}) can't be greater than the number of available parents (${allParentValues.length}).`
  )

  return allParentValues[parentDepth].value
}
