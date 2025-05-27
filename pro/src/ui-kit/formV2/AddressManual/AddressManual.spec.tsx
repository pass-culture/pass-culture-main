import { render, screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

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

  const methods = useForm<AddressManualFormValues>({
    defaultValues: initialValues,
  })

  return (
    <FormProvider {...methods}>
      <form>
        <AddressManual />
        <button type="submit">Submit</button>
      </form>
    </FormProvider>
  )
}

describe('AddressManual', () => {
  it('should render the component', () => {
    render(<TestForm />)

    // Fields must be present and required
    expect(screen.getByLabelText(/Adresse postale/)).toBeRequired()
    expect(screen.getByLabelText(/Code postal/)).toBeRequired()
    expect(screen.getByLabelText(/Ville/)).toBeRequired()
    expect(screen.getByLabelText(/Coordonnées GPS/)).toBeRequired()
  })
})
