import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { FormContact } from '../FormContact'

function renderFormContact(
  initialValues: Partial<OfferEducationalFormValues> = getDefaultEducationalValues()
) {
  function FormContactWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <FormContact disableForm={false} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormContactWrapper />)
}

describe('FormContact', () => {
  it('should show the normal contact form', () => {
    renderFormContact({})
    expect(
      screen.queryByText(
        'Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre : *'
      )
    ).not.toBeInTheDocument()
  })

  it('should show the normal contact form if the offer is bookable', () => {
    renderFormContact({ isTemplate: false })
    expect(
      screen.queryByText(
        'Choisissez le ou les moyens par lesquels vous souhaitez être contacté par les enseignants au sujet de cette offre : *'
      )
    ).not.toBeInTheDocument()
  })
})
