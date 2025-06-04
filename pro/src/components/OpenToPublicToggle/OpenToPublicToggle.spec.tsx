import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik, useFormikContext } from 'formik'
import { Form } from 'react-router'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  OpenToPublicToggle,
  OpenToPublicToggleProps,
} from './OpenToPublicToggle'

function RenderToggle({ props }: { props: Partial<OpenToPublicToggleProps> }) {
  const { handleChange } = useFormikContext()
  return <OpenToPublicToggle {...{ onChange: handleChange, ...props }} />
}

const renderOpenToPublicToggle = (
  isOpenToPublic: 'true' | 'false' = 'true',
  props: Partial<OpenToPublicToggleProps> = {}
) => {
  return renderWithProviders(
    <Formik initialValues={{ isOpenToPublic }} onSubmit={vi.fn()}>
      <Form noValidate>
        <RenderToggle props={props} />
      </Form>
    </Formik>
  )
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

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)

    const noDescription = await screen.findByText(LABELS.no.description)
    expect(noDescription).toBeInTheDocument()
  })

  it('should use custom radio descriptions', async () => {
    const customRadioDescriptions = {
      yes: 'Custom yes description',
      no: 'Custom no description',
    }

    renderOpenToPublicToggle('true', {
      radioDescriptions: customRadioDescriptions,
    })

    const yesDescription = await screen.findByText(customRadioDescriptions.yes)
    expect(yesDescription).toBeInTheDocument()

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)

    const noDescription = await screen.findByText(customRadioDescriptions.no)
    expect(noDescription).toBeInTheDocument()
  })

  it('should call onChange when a radio button is clicked', async () => {
    const onChange = vi.fn()
    renderOpenToPublicToggle('true', { onChange })

    const noRadio = await screen.findByRole('radio', { name: LABELS.no.label })
    await userEvent.click(noRadio)

    expect(onChange).toHaveBeenCalledTimes(1)
  })
})
