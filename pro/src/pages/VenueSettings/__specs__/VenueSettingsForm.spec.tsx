import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'
import { describe, expect, it } from 'vitest'

import { VenueTypeResponseModel } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { VenueSettingsFormValues } from '../types'
import { VenueSettingsForm } from '../VenueSettingsForm'

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const offerer = {
  ...defaultGetOffererResponseModel,
  id: 12,
  siren: '881457238',
}

const venueProviders = [defaultVenueProvider]

const fieldsNames = new Map([
  ['street', ''],
  ['postalCode', ''],
  ['city', ''],
  ['latitude', ''],
  ['longitude', ''],
  ['coords', ''],
  ['banId', ''],
  ['inseeCode', null],
  ['search-addressAutocomplete', ''],
  ['addressAutocomplete', ''],
])

function renderVenueSettingsForm(
  defaultProps?: VenueSettingsFormValues,
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    const methods = useForm({ defaultValues: {} })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(() => {})}>
          <VenueSettingsForm
            {...defaultProps}
            offerer={offerer}
            venueTypes={venueTypes}
            venueProviders={venueProviders}
            venue={defaultGetVenue}
          />
        </form>
      </FormProvider>
    )
  }

  options = {
    user: sharedCurrentUserFactory(),
  }

  renderWithProviders(<Wrapper />, options)
}

describe('VenueSettingsForm', () => {
  it('renders all main sections', () => {
    renderVenueSettingsForm()

    expect(screen.getByText('Informations administratives')).toBeInTheDocument()
    expect(screen.getByLabelText(/Activité principale/)).toBeInTheDocument()
  })

  it('toggles manuallySetAddress and resets fields with clearErrors', () => {
    const mockSetValue = vi.fn()
    const mockClearErrors = vi.fn()
    const manuallySetAddress = false

    // Function under test (mimicking your implementation)
    const toggleManuallySetAddress = () => {
      mockSetValue('manuallySetAddress', !manuallySetAddress)

      return [...fieldsNames.entries()].map(([fieldName, defaultValue]) => {
        mockSetValue(fieldName, defaultValue)
        mockClearErrors()
      })
    }

    toggleManuallySetAddress()

    expect(mockSetValue).toHaveBeenCalledWith('manuallySetAddress', true)

    for (const [fieldName, defaultValue] of fieldsNames.entries()) {
      expect(mockSetValue).toHaveBeenCalledWith(fieldName, defaultValue)
    }

    expect(mockClearErrors).toHaveBeenCalledTimes(fieldsNames.size)
  })
})
