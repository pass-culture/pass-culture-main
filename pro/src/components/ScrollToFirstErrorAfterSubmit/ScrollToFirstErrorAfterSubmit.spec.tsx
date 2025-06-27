import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { Button } from 'ui-kit/Button/Button'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { ScrollToFirstHookFormErrorAfterSubmit } from './ScrollToFirstErrorAfterSubmit'

const scrollIntoViewMock = vi.fn()

vi.mock('commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

function renderScrollToFirstErrorAfterSubmit() {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: { test: '' },
      mode: 'onSubmit',
    })
    const onSubmit = vi.fn()

    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <TextInput name="test" label="test" />
          <Button type="submit">Enregistrer</Button>
          <ScrollToFirstHookFormErrorAfterSubmit />
        </form>
      </FormProvider>
    )
  }

  render(<Wrapper />)
}

describe('ScrollToFirstHookFormErrorAfterSubmit', () => {
  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    scrollIntoViewMock.mockClear()
  })

  it('should scroll into view and give focus on first error field', async () => {
    renderScrollToFirstErrorAfterSubmit()

    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer' }))

    await waitFor(() => {
      expect(screen.getByText('Veuillez remplir le champ')).toBeInTheDocument()
    })

    expect(scrollIntoViewMock).toHaveBeenCalled()
    expect(screen.getByLabelText(/test/i)).toHaveFocus()
  })
})
