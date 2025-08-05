import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { FormProvider, useForm } from 'react-hook-form'

import { FormAccessibility } from './FormAccessibility'

function renderFormAccessibility(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function FormAccessibilityWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <FormAccessibility disableForm={false} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormAccessibilityWrapper />)
}

describe('FormAccessibility', () => {
  it('should uncheck all accessibility checkboxes when none is checked', async () => {
    renderFormAccessibility({
      accessibility: {
        audio: true,
        mental: true,
        motor: true,
        none: false,
        visual: true,
      },
    })

    expect(screen.getByLabelText('Auditif')).toBeChecked()
    expect(screen.getByLabelText('Psychique ou cognitif')).toBeChecked()
    expect(screen.getByLabelText('Moteur')).toBeChecked()
    expect(screen.getByLabelText('Visuel')).toBeChecked()

    await userEvent.click(screen.getByLabelText('Non accessible'))

    expect(screen.getByLabelText('Auditif')).not.toBeChecked()
    expect(screen.getByLabelText('Psychique ou cognitif')).not.toBeChecked()
    expect(screen.getByLabelText('Moteur')).not.toBeChecked()
    expect(screen.getByLabelText('Visuel')).not.toBeChecked()
  })

  it('should uncheck none when an accessibility checkbox is checked', async () => {
    renderFormAccessibility({
      accessibility: {
        audio: false,
        mental: false,
        motor: false,
        none: true,
        visual: false,
      },
    })

    expect(screen.getByLabelText('Non accessible')).toBeChecked()

    await userEvent.click(screen.getByLabelText('Auditif'))

    expect(screen.getByLabelText('Non accessible')).not.toBeChecked()
  })
})
