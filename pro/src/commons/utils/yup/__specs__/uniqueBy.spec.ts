import { yup } from '../index'

describe('yup.array().uniqueBy', () => {
  const base = yup.mixed().nullable().optional()

  it('should return true when string values are unique by key', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup')
    const data = [{ code: 'A' }, { code: 'B' }, { code: 'C' }]

    expect(schema.isValidSync(data)).toBe(true)
  })

  it('should return false when string values are duplicated by key', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup')
    const data = [{ code: 'A' }, { code: 'A' }]

    expect(schema.isValidSync(data)).toBe(false)
  })

  it('should return false when number values are duplicated by key', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup')
    const data = [{ code: 1 }, { code: 2 }, { code: 1 }]

    expect(schema.isValidSync(data)).toBe(false)
  })

  it('should ignore nullish items and nullish key values', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup')
    const data = [
      null,
      undefined,
      { code: null },
      { code: undefined },
      { code: 'A' },
      { code: 'B' },
      { code: 1 },
      { code: 2 },
    ]

    expect(schema.isValidSync(data)).toBe(true)
  })

  it('should ignore non string/number key values without failing', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup')
    const data = [{ code: { foo: 'bar' } }, { code: { foo: 'bar' } }]

    expect(schema.isValidSync(data)).toBe(true)
  })

  it('should use the provided custom message on failure', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'Dup key')
    const data = [{ code: 'X' }, { code: 'X' }]

    try {
      schema.validateSync(data)
      expect(true).toBe(false)
    } catch (e: unknown) {
      const err = e as yup.ValidationError
      expect(err.inner.length).toBe(2)
      expect(err.inner.every((ie) => ie.message === 'Dup key')).toBe(true)
    }
  })

  it('should set errors at each offending item index', () => {
    const schema = yup.array().of(base).uniqueBy('code', 'dup-message')
    const data = [{ code: 'A' }, { code: 'B' }, { code: 'A' }, { code: 'B' }]

    try {
      schema.validateSync(data, { abortEarly: false })
      expect(true).toBe(false)
    } catch (e: unknown) {
      const err = e as yup.ValidationError
      const paths = (err.inner?.length ? err.inner : [err])
        .map((x) => x.path)
        .filter((p): p is string => Boolean(p))
        .sort()
      expect(paths).toEqual(['[0]', '[1]', '[2]', '[3]'])
      expect(err.inner.every((ie) => ie.message === 'dup-message')).toBe(true)
    }
  })
})
