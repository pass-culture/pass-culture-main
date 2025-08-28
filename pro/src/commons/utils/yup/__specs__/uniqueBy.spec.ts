import { yup } from '../index'

describe('yup.array().uniqueBy', () => {
  const nullableOptionalMixedSchema = yup.mixed().nullable().optional()

  it('should return true when string values are unique by key', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')
    const testData = [{ code: 'A' }, { code: 'B' }, { code: 'C' }]

    expect(schema.isValidSync(testData)).toBe(true)
  })

  it('should return false when string values are duplicated by key', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')

    const testData = [{ code: 'A' }, { code: 'A' }]

    expect(schema.isValidSync(testData)).toBe(false)
  })

  it('should return false when number values are duplicated by key', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')

    const testData = [{ code: 1 }, { code: 2 }, { code: 1 }]

    expect(schema.isValidSync(testData)).toBe(false)
  })

  it('should ignore nullish items and nullish key values', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')

    const testData = [
      { code: null },
      { code: undefined },
      { code: 'A' },
      { code: 'B' },
      { code: 1 },
      { code: 2 },
    ]

    expect(schema.isValidSync(testData)).toBe(true)
  })

  it('should ignore non string/number key values without failing', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')

    const testData = [{ code: { foo: 'bar' } }, { code: { foo: 'bar' } }]

    expect(schema.isValidSync(testData)).toBe(true)
  })

  it('should use the provided custom message on failure', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique.')
    const testData = [{ code: 'X' }, { code: 'X' }]

    try {
      schema.validateSync(testData)

      expect(true).toBe(false)
    } catch (error: unknown) {
      const validationError = error as yup.ValidationError

      expect(validationError.inner.length).toBe(1)
      expect(
        validationError.inner.every(
          (innerError) => innerError.message === 'Codes must be unique.'
        )
      ).toBe(true)
    }
  })

  it('should set errors at each offending item index', () => {
    const schema = yup
      .array()
      .of(nullableOptionalMixedSchema)
      .uniqueBy('code', 'Codes must be unique')

    const testData = [
      { code: 'A' },
      { code: 'B' },
      { code: 'A' },
      { code: 'B' },
    ]

    try {
      schema.validateSync(testData, { abortEarly: false })

      expect(true).toBe(false)
    } catch (error: unknown) {
      const validationError = error as yup.ValidationError
      const errorPaths = (
        validationError.inner?.length
          ? validationError.inner
          : [validationError]
      )
        .map((errorDetail) => errorDetail.path)
        .filter((path): path is string => Boolean(path))
        .sort()

      expect(errorPaths).toEqual(['[2].code', '[3].code'])
      expect(
        validationError.inner.every(
          (innerError) => innerError.message === 'Codes must be unique'
        )
      ).toBe(true)
    }
  })
})
