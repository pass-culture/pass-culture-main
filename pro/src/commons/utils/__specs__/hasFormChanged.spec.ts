import { hasFormChanged } from '../hasFormChanged'

describe('hasFormChanged', () => {
  it('should return true if any field is touched and its value has changed from initial values', () => {
    const form = {
      getFieldState: vi.fn().mockReturnValue({ isTouched: true }),
      getValues: vi.fn().mockReturnValue('new value'),
      // biome-ignore lint/suspicious/noExplicitAny: This is an external lib type mock.
    } as any
    const initialValues = { aField: 'initial value' }
    const fields: Array<keyof typeof initialValues> = ['aField']

    const result = hasFormChanged({ form, fields, initialValues })

    expect(result).toBe(true)
  })

  it('should return false if any field is touched and touched fields have not changed', () => {
    const form = {
      getFieldState: vi.fn().mockReturnValue({ isTouched: true }),
      getValues: vi.fn().mockReturnValue('initial value'),
      // biome-ignore lint/suspicious/noExplicitAny: This is an external lib type mock.
    } as any
    const initialValues = { aField: 'initial value' }
    const fields: Array<keyof typeof initialValues> = ['aField']

    const result = hasFormChanged({ form, fields, initialValues })

    expect(result).toBe(false)
  })

  it('should return false if no fields are touched', () => {
    const form = {
      getFieldState: vi.fn().mockReturnValue({ isTouched: false }),
      getValues: vi.fn(),
      // biome-ignore lint/suspicious/noExplicitAny: This is an external lib type mock.
    } as any
    const initialValues = { aField: 'initial value' }
    const fields: Array<keyof typeof initialValues> = ['aField']

    const result = hasFormChanged({ form, fields, initialValues })

    expect(result).toBe(false)
  })
})
