import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import {
  OpenToPublicToggle,
  type OpenToPublicToggleProps,
} from './OpenToPublicToggle'

const onChange = vi.fn()

function renderOpenToPublicToggle(
  isOpenToPublic: 'true' | 'false' = 'true',
  props: Partial<OpenToPublicToggleProps> = {}
) {
  const Wrapper = () => {
    const methods = useForm({ defaultValues: {} })
    return (
      <FormProvider {...methods}>
        <OpenToPublicToggle
          {...props}
          isOpenToPublic={isOpenToPublic}
          onChange={onChange}
        />
      </FormProvider>
    )
  }

  render(<Wrapper />)
}

const LABELS = {
  yes: {
    label: /Oui/,
  },
  no: {
    label: /Non/,
  },
}

describe('OpenToPublicToggle', () => {
  it('should render two radio buttons to toggle open to public', async () => {
    renderOpenToPublicToggle()

    const yesRadio = await screen.findByRole('radio', {
      name: LABELS.yes.label,
    })
    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })

    expect(yesRadio).toBeInTheDocument()
    expect(noRadio).toBeInTheDocument()
  })

  it('should display a description if provided', async () => {
    renderOpenToPublicToggle('true', {
      overrideDescription: 'This is a description',
    })

    const description = await screen.findByText('This is a description')
    expect(description).toBeInTheDocument()

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)
    expect(description).toBeInTheDocument()
  })

  it('should call onChange when a radio button is clicked', async () => {
    renderOpenToPublicToggle('true')

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)

    expect(onChange).toHaveBeenCalledTimes(1)
  })
})
