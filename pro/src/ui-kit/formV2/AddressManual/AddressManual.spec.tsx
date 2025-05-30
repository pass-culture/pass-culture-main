import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { describe, it, vi } from 'vitest'

import { AddressManual } from './AddressManual'

// Mock utils used inside component
vi.mock('commons/utils/coords', () => ({
  getCoordsType: (input: string) => (input.includes('°') ? 'DMS' : 'DD'),
  parseDms: (dms: string) => {
    if (dms === `48°51'12.0"N`) {
      return 48.85333
    }
    if (dms === `2°20'56.3"E`) {
      return 2.34897
    }
    return 0
  },
}))

describe('AddressManual', () => {
  it('renders and handles coords input blur event with userEvent', async () => {
    const Wrapper = () => {
      const methods = useForm({
        defaultValues: {
          street: '',
          postalCode: '',
          city: '',
          coords: '',
          latitude: '',
          longitude: '',
        },
      })

      return (
        <FormProvider {...methods}>
          <AddressManual />
        </FormProvider>
      )
    }

    render(<Wrapper />)

    const coordsInput = screen.getByLabelText(/Coordonnées GPS/i)

    // Type decimal degrees and trigger blur
    await userEvent.clear(coordsInput)
    await userEvent.type(coordsInput, '48.853320, 2.348979')
    await userEvent.tab() // blur

    // Type DMS and trigger blur
    await userEvent.clear(coordsInput)
    await userEvent.type(coordsInput, `48°51'12.0"N 2°20'56.3"E`)
    await userEvent.tab() // blur
  })
})
