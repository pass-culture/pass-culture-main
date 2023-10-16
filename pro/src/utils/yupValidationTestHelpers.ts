import * as yup from 'yup'

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

const hasFromAttribute = (
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
  if (!hasFromAttribute(testContext)) {
    throw new Error('TestContext is not valid')
  }
  const allParentValues = testContext.from

  if (allParentValues.length < parentDepth) {
    throw new Error('Parent depth is not valid')
  }

  return allParentValues[parentDepth]?.value
}
