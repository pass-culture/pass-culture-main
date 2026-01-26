import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import type { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { mainlandOptions } from '@/commons/core/shared/interventionOptions'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { InterventionAreaMultiSelect } from '../InterventionAreaMultiSelect'

function renderInterventionAreaMultiSelect(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function InterventionAreaMultiSelectWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <InterventionAreaMultiSelect
          disabled={false}
          label="sélectionnez des départements"
        />
      </FormProvider>
    )
  }

  return renderWithProviders(<InterventionAreaMultiSelectWrapper />)
}

describe('InterventionAreaMultiSelect', () => {
  it('should render correctly', () => {
    renderInterventionAreaMultiSelect({ interventionArea: ['75', '44'] })

    expect(
      screen.getByText('sélectionnez des départements *')
    ).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('Département(s)')).toBeInTheDocument()
    expect(screen.getByText('44 - Loire-Atlantique')).toBeInTheDocument()
    expect(screen.getByText('75 - Paris')).toBeInTheDocument()
  })

  it('should check all mainland departments when checking mainland', async () => {
    renderInterventionAreaMultiSelect({ interventionArea: [] })

    const departmentButton = screen.getByLabelText('Département(s)')
    await userEvent.click(departmentButton)

    const mainlandCheckbox = screen.getByLabelText('France métropolitaine')
    await userEvent.click(mainlandCheckbox)

    expect(mainlandCheckbox).toBeChecked()

    mainlandOptions.forEach((departmentOption) => {
      const departmentCheckbox = screen.getByLabelText(departmentOption.label)
      expect(departmentCheckbox).toBeChecked()
    })
  })

  it('should uncheck mainland option when a department is unchecked', async () => {
    renderInterventionAreaMultiSelect({
      interventionArea: [
        ...mainlandOptions.map((value) => value.id),
        'mainland',
      ],
    })
    const departmentButton = screen.getByLabelText('Département(s)')
    await userEvent.click(departmentButton)

    const mainlandCheckbox = screen.getByLabelText('France métropolitaine')
    expect(mainlandCheckbox).toBeChecked()

    const parisCheckbox = screen.getByLabelText('75 - Paris')
    await userEvent.click(parisCheckbox)

    expect(mainlandCheckbox).not.toBeChecked()
  })
})
