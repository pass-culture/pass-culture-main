import { Form, FormikProvider, useFormik } from 'formik'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { DetailsForm } from './DetailsForm'
import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'

type DetailsScreenProps = {}

export const DetailsScreen = ({}: DetailsScreenProps): JSX.Element => {
  const formik = useFormik({
    initialValues: DEFAULT_DETAILS_INTITIAL_VALUES,
    onSubmit: () => {},
  })

  return (
    <FormikProvider value={formik}>
      <Form>
        <FormLayout fullWidthActions>
          <FormLayout.MandatoryInfo />
          <DetailsForm />
        </FormLayout>
      </Form>
    </FormikProvider>
  )
}
