import { render, screen } from '@testing-library/react'
import { Form, FormikProvider, useFormik } from 'formik'

import { AddressManual } from './AddressManual'

interface AddressManualFormValues {
  street: string
  postalCode: string
  city: string
  coords: string
  latitude: string
  longitude: string
}

const TestForm = (): JSX.Element => {
  const initialValues: AddressManualFormValues = {
    street: '',
    postalCode: '',
    city: '',
    coords: '',
    latitude: '',
    longitude: '',
  }

  const formik = useFormik<AddressManualFormValues>({
    initialValues: initialValues,
    onSubmit: vi.fn(),
  })

  return (
    <FormikProvider value={formik}>
      <Form>
        <AddressManual />
        <button type="submit">Submit</button>
      </Form>
    </FormikProvider>
  )
}

describe('AddressManual', () => {
  it('should render the component', () => {
    render(<TestForm />)

    // Fields must be present and required
    expect(screen.getByLabelText(/Adresse postale/)).not.toBeRequired()
    expect(screen.getByLabelText(/Code postal/)).toBeRequired()
    expect(screen.getByLabelText(/Ville/)).toBeRequired()
    expect(screen.getByLabelText(/Coordonnées GPS/)).toBeRequired()
  })
})
