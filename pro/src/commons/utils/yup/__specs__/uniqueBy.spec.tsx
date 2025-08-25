import { yupResolver } from '@hookform/resolvers/yup'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useForm } from 'react-hook-form'

import { yup } from '../index'

interface Item {
  code?: string | number | null
}
interface FormValues {
  items: Item[]
}

const schema = yup
  .object({
    items: yup
      .array()
      .of(yup.mixed<Item>().defined())
      .uniqueBy('code', 'duplicate')
      .required(),
  })
  .required()

const LABELS = {
  add: 'Add',
  submit: 'Submit',
}

function TestForm({ onSubmit }: { onSubmit: (data: FormValues) => void }) {
  const { register, handleSubmit, setValue } = useForm<FormValues>({
    resolver: yupResolver(schema),
    defaultValues: { items: [] },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('items.0.code' as const)} data-testid="code-0" />
      <input {...register('items.1.code' as const)} data-testid="code-1" />
      <button type="button" onClick={() => setValue('items', [])}>
        {LABELS.add}
      </button>
      <button type="submit">{LABELS.submit}</button>
    </form>
  )
}

describe('yup.array().uniqueBy  (react-hook-form)', () => {
  it('accepts unique values and rejects duplicates', async () => {
    const onSubmit = vi.fn()
    render(<TestForm onSubmit={onSubmit} />)

    await userEvent.type(screen.getByTestId('code-0'), 'A')
    await userEvent.type(screen.getByTestId('code-1'), 'B')

    await userEvent.click(screen.getByRole('button', { name: LABELS.submit }))
    expect(onSubmit).toHaveBeenCalledWith(
      { items: [{ code: 'A' }, { code: 'B' }] },
      expect.anything()
    )

    onSubmit.mockClear()

    // Now duplicate
    await userEvent.clear(screen.getByTestId('code-1'))
    await userEvent.type(screen.getByTestId('code-1'), 'A')

    await userEvent.click(screen.getByRole('button', { name: LABELS.submit }))
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
