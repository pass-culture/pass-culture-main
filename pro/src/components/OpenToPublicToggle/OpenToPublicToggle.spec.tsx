import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import {
  OpenToPublicToggle,
  OpenToPublicToggleProps,
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
    label: 'Oui',
    description: 'Votre adresse postale sera visible.',
  },
  no: {
    label: 'Non',
    description: 'Votre adresse postale ne sera pas visible.',
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

  it('should display a description based on the selected radio button', async () => {
    renderOpenToPublicToggle('true')

    const yesDescription = await screen.findByText(LABELS.yes.description)
    expect(yesDescription).toBeInTheDocument()
  })

  it('should use custom radio descriptions for yes', async () => {
    const onChange = vi.fn()

    const customRadioDescriptions = {
      yes: 'Custom yes description',
      no: 'Custom no description',
    }

    renderOpenToPublicToggle('true', {
      radioDescriptions: customRadioDescriptions,
      onChange,
    })

    const yesDescription = await screen.findByText(customRadioDescriptions.yes)
    expect(yesDescription).toBeInTheDocument()
  })

  it('should use custom radio descriptions for no', async () => {
    const onChange = vi.fn()

    const customRadioDescriptions = {
      yes: 'Custom yes description',
      no: 'Custom no description',
    }

    renderOpenToPublicToggle('false', {
      radioDescriptions: customRadioDescriptions,
      onChange,
    })

    const yesDescription = await screen.findByText(customRadioDescriptions.no)
    expect(yesDescription).toBeInTheDocument()
  })

  it('should call onChange when a radio button is clicked', async () => {
    renderOpenToPublicToggle('true')

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)

    expect(onChange).toHaveBeenCalledTimes(1)
  })
})
