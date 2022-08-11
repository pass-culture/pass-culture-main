import { FormikProvider, useFormik } from 'formik'
import React from 'react'

import {
  VenueForm,
  validationSchema,
  IVenueFormValues,
} from 'new_components/VenueForm'
import { Title } from 'ui-kit'

interface IVenueEditionProps {
  initialValues: IVenueFormValues
}

const VenueEdition = ({ initialValues }: IVenueEditionProps): JSX.Element => {
  const onSubmit = () => {
    alert('todo submit form !')
  }

  const formik = useFormik({
    initialValues,
    onSubmit,
    validationSchema,
  })

  return (
    <div>
      <Title level={1}>Lieu</Title>
      {initialValues.publicName && (
        <Title level={2}>{initialValues.publicName}</Title>
      )}

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueForm />
        </form>
      </FormikProvider>
    </div>
  )
}

export default VenueEdition
