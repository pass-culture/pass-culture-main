import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { vi } from 'vitest'

import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  individualOfferContextValuesFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { makeLocationFormValues } from '../../../commons/__mocks__/makeLocationFormValues'
import type { LocationFormValues } from '../../../commons/types'
import {
  PhysicalLocationSubform,
  type PhysicalLocationSubformProps,
} from './PhysicalLocationSubform'

// Mock AddressSelect to avoid triggering real fetch / side effects (BAN API autocomplete) in unit tests
// TODO Fetch is already globally mocked in vitest.setup.ts, rather mock and spy on the api calls than the entire component.
vi.mock('@/ui-kit/form/AddressSelect/AddressSelect', () => ({
  AddressSelect: ({
    label,
    disabled,
    onChange,
    value = '',
  }: {
    label: string
    disabled?: boolean
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
    value?: string | null
  }) => (
    <input
      aria-label={label}
      role="combobox"
      disabled={disabled}
      value={value ?? ''}
      onChange={(e) => onChange?.(e)}
    />
  ),
}))
vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))
vi.mock('@/commons/errors/FrontendError', () => ({
  FrontendError: class FrontendError extends Error {},
}))

type ExtraParams = { formDefaults?: Partial<LocationFormValues> }

const renderPhysicalLocationSubform: RenderComponentFunction<
  PhysicalLocationSubformProps,
  IndividualOfferContextValues,
  ExtraParams
> = ({ contextValues, options, props, formDefaults }) => {
  const venue: VenueListItemResponseModel = props?.venue
    ? (props.venue as VenueListItemResponseModel)
    : makeVenueListItem({
        id: 2,
        location: {
          id: 10,
          city: 'Paris',
          isManualEdition: false,
          label: '10 Rue de Paris 75000 Paris',
          postalCode: '75000',
          street: '10 Rue de Paris',
          latitude: 48.8566,
          longitude: 2.3522,
          isVenueLocation: false,
        },
      })

  const defaultValues = makeLocationFormValues({
    location: {
      addressAutocomplete: null,
      banId: null,
      city: 'Paris',
      coords: '48.8566, 2.3522',
      inseeCode: null,
      isManualEdition: false,
      isVenueLocation: true,
      label: null,
      latitude: '48.8566',
      longitude: '2.3522',
      offerLocation: venue.location?.id?.toString() || '',
      postalCode: '75000',
      'search-addressAutocomplete': null,
      street: '10 Rue de Paris',
    },
    ...formDefaults,
  })

  const Wrapper = () => {
    const methods = useForm<LocationFormValues>({ defaultValues })
    return (
      <FormProvider {...methods}>
        <PhysicalLocationSubform
          isDisabled={props?.isDisabled ?? false}
          venue={venue}
        />
      </FormProvider>
    )
  }

  const contextValue = {
    ...individualOfferContextValuesFactory(),
    ...contextValues,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <Wrapper />
    </IndividualOfferContext.Provider>,
    { user: sharedCurrentUserFactory(), ...options }
  )
}

describe('<PhysicalLocationSubform />', () => {
  it('should show venue address radio selected by default (no other address fields)', () => {
    renderPhysicalLocationSubform({})

    expect(
      screen.getByRole('radio', { name: /10 Rue de Paris 75000 Paris/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText(/Intitulé de la localisation/i)
    ).not.toBeInTheDocument()
  })

  it('should switch to other address fields when selecting other address', async () => {
    //  Catch an error that only seems to appear in tests:
    // `Warning: Function components cannot be given refs. Attempts to access this ref will fail. Did you mean to use React.forwardRef()?`
    // This may be related to `AddressSelect` implementation.
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    renderPhysicalLocationSubform({})

    await userEvent.click(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    )

    expect(consoleErrorSpy).toHaveBeenCalledOnce()

    expect(
      screen.getByLabelText(/Intitulé de la localisation/i)
    ).toBeInTheDocument()
  })

  it('should toggle back to venue address and hide other address fields', async () => {
    renderPhysicalLocationSubform({})

    await userEvent.click(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    )
    expect(
      screen.getByLabelText(/Intitulé de la localisation/i)
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: /10 Rue de Paris 75000 Paris/i })
    )

    expect(
      screen.queryByLabelText(/Intitulé de la localisation/i)
    ).not.toBeInTheDocument()
  })

  it('should enable manual edition and display manual address fields', async () => {
    renderPhysicalLocationSubform({
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: false,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })
    await userEvent.click(
      screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/i,
      })
    )
    // Street manual field becomes available (textbox) while original combobox (role=combobox) stays
    expect(
      screen.getByRole('textbox', { name: /Adresse postale/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('combobox', { name: /Adresse postale/i })
    ).toBeDisabled()
  })

  it('should reset address fields when switching from venue to other address', async () => {
    renderPhysicalLocationSubform({})

    await userEvent.click(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/i,
      })
    )

    const streetInput = screen.getByRole<HTMLInputElement>('textbox', {
      name: /Adresse postale/i,
    })
    expect(streetInput.value).toBe('')
  })

  it('should toggle manual edition off and hide manual fields keeping other address mode', async () => {
    renderPhysicalLocationSubform({
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: false,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/i,
      })
    )

    expect(
      screen.getAllByLabelText(/Adresse postale/i).length
    ).toBeGreaterThanOrEqual(1)
    await userEvent.click(
      await screen.findByRole('button', {
        name: /Revenir à la sélection automatique/i,
      })
    )

    // Manual street textbox should be gone, but combobox (Adresse postale) should still be present
    expect(
      screen.getByRole('combobox', { name: /Adresse postale/i })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('textbox', { name: /Adresse postale/i })
    ).not.toBeInTheDocument()
    expect(
      screen.getByLabelText(/Intitulé de la localisation/i)
    ).toBeInTheDocument()
  })

  it('should disable address select (combobox) when manual edition is enabled and keep manual street input enabled', async () => {
    renderPhysicalLocationSubform({
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: false,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })
    expect(
      screen.getByRole<HTMLInputElement>('combobox', {
        name: /Adresse postale/i,
      })
    ).not.toBeDisabled()

    await userEvent.click(
      screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/i,
      })
    )

    const postaleFields = screen.getAllByLabelText(/Adresse postale/i)
    expect(postaleFields.length).toBeGreaterThanOrEqual(2)

    expect(
      screen.getByRole<HTMLInputElement>('combobox', {
        name: /Adresse postale/i,
      })
    ).toBeDisabled()

    const manualStreet = screen.getByRole('textbox', {
      name: /Adresse postale/,
    })
    expect(manualStreet).toBeDefined()
    expect(manualStreet).not.toBeDisabled()
  })

  it('should respect isDisabled prop (all interactive elements disabled)', () => {
    renderPhysicalLocationSubform({
      props: { isDisabled: true },
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: true,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })

    expect(
      screen.getByRole('textbox', { name: 'Intitulé de la localisation' })
    ).toBeDisabled()

    expect(
      screen.getByRole('button', {
        name: /Revenir à la sélection automatique/i,
      })
    ).toBeDisabled()

    const postaleFields = screen.getAllByLabelText(/Adresse postale/i)
    postaleFields.forEach((el) => {
      expect(el).toBeDisabled()
    })
  })

  it('should not switch to other address when radiogroup is disabled', async () => {
    renderPhysicalLocationSubform({
      props: { isDisabled: true },
    })

    // Attempt click
    await userEvent.click(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    )

    // Other address fields should remain hidden
    expect(screen.queryByLabelText(/Intitulé de la localisation/i)).toBeFalsy()
  })

  it('should not enable manual edition when button is disabled', async () => {
    renderPhysicalLocationSubform({
      props: { isDisabled: true },
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: false,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })

    const manualBtn = screen.getByRole('button', {
      name: /Vous ne trouvez pas votre adresse/i,
    })
    expect(manualBtn).toBeDisabled()
    await userEvent.click(manualBtn)
    // Manual textbox should not appear
    expect(
      screen.queryByRole('textbox', { name: /Adresse postale/i })
    ).not.toBeInTheDocument()
  })

  it('should call handleUnexpectedError when toggling back to venue address but venue.address is missing', async () => {
    const { handleUnexpectedError } = await import(
      '@/commons/errors/handleUnexpectedError'
    )
    // Start on venue address, go to other, then back (error path when venue.address is undefined)
    const venueWithoutAddress = makeVenueListItem({
      id: 2,
      location: undefined,
    })
    renderPhysicalLocationSubform({
      props: {
        venue: venueWithoutAddress as unknown as VenueListItemResponseModel,
      },
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: '',
          coords: '',
          inseeCode: null,
          isManualEdition: false,
          isVenueLocation: true,
          label: null,
          latitude: '',
          longitude: '',
          offerLocation: '',
          postalCode: '',
          'search-addressAutocomplete': null,
          street: '',
        },
      },
    })

    // First click switches to other address
    await userEvent.click(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    )
    expect(
      screen.getByLabelText(/Intitulé de la localisation/i)
    ).toBeInTheDocument()

    // Second click attempts to switch back to venue address triggering error
    await userEvent.click(screen.getByRole('radio', { name: / – null/i }))
    expect(handleUnexpectedError).toHaveBeenCalled()
  })

  it('should render manual edition fields on mount when defaults set isManualEdition=true', () => {
    renderPhysicalLocationSubform({
      formDefaults: {
        location: {
          addressAutocomplete: null,
          banId: null,
          city: 'Paris',
          coords: '',
          inseeCode: null,
          isManualEdition: true,
          isVenueLocation: false,
          label: null,
          latitude: '48.8566',
          longitude: '2.3522',
          offerLocation: 'other',
          postalCode: '75000',
          'search-addressAutocomplete': null,
          street: '10 Rue de Paris',
        },
      },
    })

    expect(
      screen.getByRole('textbox', { name: /Adresse postale/i })
    ).toBeInTheDocument()
  })
})
