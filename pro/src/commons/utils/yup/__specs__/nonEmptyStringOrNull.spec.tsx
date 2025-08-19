import { yupResolver } from '@hookform/resolvers/yup'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'
import { object } from 'yup'

import { nonEmptyStringOrNull } from '../nonEmptyStringOrNull'

// We use this type to ensure TS inferences correctly.
interface FormValues {
  testField: string | null
}

const schema = object<FormValues>().shape({
  testField: nonEmptyStringOrNull(),
})

describe('nonEmptyStringOrNull (react-hook-form)', () => {
  const TestComponent = ({
    onSubmit,
    initialValue,
  }: {
    onSubmit: (data: FormValues) => void
    initialValue?: string | null
  }) => {
    // Specifying the generic here prevents `useForm` from internally making props "undefinedable" via `| undefined`.
    const { register, handleSubmit } = useForm<FormValues>({
      resolver: yupResolver(schema),
      defaultValues: { testField: initialValue },
    })

    return (
      <form onSubmit={handleSubmit(onSubmit)}>
        <input {...register('testField')} data-testid="test-input" />
        <button type="submit">Submit</button>
      </form>
    )
  }

  it('should submit with the initial non-empty string value', async () => {
    const onSubmit = vi.fn()

    render(<TestComponent onSubmit={onSubmit} initialValue="initial" />)

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(onSubmit).toHaveBeenCalledWith(
      { testField: 'initial' },
      expect.anything()
    )
  })

  it('should submit with null when initial value is an empty string', async () => {
    const onSubmit = vi.fn()

    render(<TestComponent onSubmit={onSubmit} initialValue="" />)

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(onSubmit).toHaveBeenCalledWith(
      { testField: null },
      expect.anything()
    )
  })

  it('should submit with null when initial value is null', async () => {
    const onSubmit = vi.fn()

    render(<TestComponent onSubmit={onSubmit} initialValue={null} />)

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(onSubmit).toHaveBeenCalledWith(
      { testField: null },
      expect.anything()
    )
  })

  it('should submit with a typed value', async () => {
    const onSubmit = vi.fn()

    render(<TestComponent onSubmit={onSubmit} />)
    const input = screen.getByTestId('test-input')

    await userEvent.type(input, 'new value')
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(onSubmit).toHaveBeenCalledWith(
      { testField: 'new value' },
      expect.anything()
    )
  })

  it('should submit with null after clearing the input', async () => {
    const onSubmit = vi.fn()

    render(<TestComponent onSubmit={onSubmit} initialValue="initial" />)
    const input = screen.getByTestId('test-input')

    await userEvent.clear(input)
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(onSubmit).toHaveBeenCalledWith(
      { testField: null },
      expect.anything()
    )
  })
})
