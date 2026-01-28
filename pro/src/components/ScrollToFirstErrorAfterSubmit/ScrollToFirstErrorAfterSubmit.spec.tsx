import { yupResolver } from '@hookform/resolvers/yup'
import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import * as yup from 'yup'

import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'

import { ScrollToFirstHookFormErrorAfterSubmit } from './ScrollToFirstErrorAfterSubmit'

const scrollIntoViewMock = vi.fn()
const onSubmit = vi.fn()

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

const schema = yup.object({
  firstName: yup.string().required('Veuillez remplir le champ'),
})

function renderScrollToFirstErrorAfterSubmit() {
  function Wrapper() {
    const form = useForm({
      defaultValues: { firstName: '' },
      resolver: yupResolver(schema),
    })

    return (
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <ScrollToFirstHookFormErrorAfterSubmit />

          <TextInput
            label="firstName"
            required={true}
            {...form.register('firstName')}
            error={form.formState.errors.firstName?.message}
          />
          <Button type="submit" label="Enregistrer"></Button>
        </form>
      </FormProvider>
    )
  }

  return {
    ...render(<Wrapper />),
  }
}

describe('ScrollToFirstErrorAfterSubmit', () => {
  it('should scroll into view and give focus', async () => {
    Element.prototype.scrollIntoView = scrollIntoViewMock

    renderScrollToFirstErrorAfterSubmit()

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(screen.getByText('Veuillez remplir le champ')).toBeInTheDocument()
      expect(scrollIntoViewMock).toHaveBeenCalled()
    })

    expect(screen.getByLabelText(/firstName/)).toHaveFocus()
  })
})
