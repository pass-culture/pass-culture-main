import { useFormikContext } from 'formik'
import React from 'react'

import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import { Informations } from './Informations'

const VenueForm = () => {
  const { isSubmitting } = useFormikContext()
  return (
    <div>
      <FormLayout>
        <Informations />

        <SubmitButton isLoading={isSubmitting}>Valider</SubmitButton>
      </FormLayout>
    </div>
  )
}

export default VenueForm
