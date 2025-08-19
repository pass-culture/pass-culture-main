import { object } from 'yup'

import { nonEmptyStringOrNull } from '../nonEmptyStringOrNull'

const schema = object({
  testField: nonEmptyStringOrNull(),
})

describe('nonEmptyStringOrNull', () => {
  it('should return null for undefined', async () => {
    const result = await schema.validate({ testField: undefined })

    expect(result.testField).toBeNull()
  })

  it('should return null for an empty string', async () => {
    const result = await schema.validate({ testField: '' })

    expect(result.testField).toBeNull()
  })

  it('should return null for a whitespace string', async () => {
    const result = await schema.validate({ testField: '   ' })

    expect(result.testField).toBeNull()
  })

  it('should return the string for a non-empty string', async () => {
    const result = await schema.validate({ testField: 'hello' })

    expect(result.testField).toBe('hello')
  })

  it('should return null for a null value', async () => {
    const result = await schema.validate({ testField: null })

    expect(result.testField).toBeNull()
  })
})
