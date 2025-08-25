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
  }: {
    label: string
    disabled?: boolean
  }) => <input aria-label={label} role="combobox" disabled={disabled} />,
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
        address: {
          id: 1,
          id_oa: 10,
          city: 'Paris',
          isManualEdition: false,
          label: '10 Rue de Paris 75000 Paris',
          postalCode: '75000',
          street: '10 Rue de Paris',
          latitude: 48.8566,
          longitude: 2.3522,
        },
      })

  const defaultValues = makeLocationFormValues({
    address: {
      addressAutocomplete: null,
      banId: null,
      city: 'Paris',
      coords: '48.8566, 2.3522',
      inseeCode: null,
      isManualEdition: false,
      isVenueAddress: true,
      latitude: '48.8566',
      locationLabel: null,
      longitude: '2.3522',
      offerLocation: venue.address?.id_oa?.toString() || '',
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

describe('PhysicalLocationSubform (new)', () => {
  describe('initial state', () => {
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
      renderPhysicalLocationSubform({})

      const otherRadio = screen.getByRole('radio', {
        name: 'À une autre adresse',
      })
      await userEvent.click(otherRadio)

      expect(
        screen.getByLabelText(/Intitulé de la localisation/i)
      ).toBeInTheDocument()
    })
  })

  describe('manual edition', () => {
    it('should enable manual edition and display manual address fields', async () => {
      renderPhysicalLocationSubform({
        formDefaults: {
          address: {
            addressAutocomplete: null,
            banId: null,
            city: 'Paris',
            coords: null,
            inseeCode: null,
            isManualEdition: false,
            isVenueAddress: false,
            latitude: '48.8566',
            locationLabel: null,
            longitude: '2.3522',
            offerLocation: 'other',
            postalCode: '75000',
            'search-addressAutocomplete': null,
            street: '10 Rue de Paris',
          },
        },
      })

      const manualButton = screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/i,
      })
      await userEvent.click(manualButton)
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
      const streetInput = screen.getByRole('textbox', {
        name: /Adresse postale/i,
      }) as HTMLInputElement
      expect(streetInput.value).toBe('')
    })

    it('should toggle manual edition off and hide manual fields keeping other address mode', async () => {
      renderPhysicalLocationSubform({
        formDefaults: {
          address: {
            addressAutocomplete: null,
            banId: null,
            city: 'Paris',
            coords: null,
            inseeCode: null,
            isManualEdition: false,
            isVenueAddress: false,
            latitude: '48.8566',
            locationLabel: null,
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

      const backButton = await screen.findByRole('button', {
        name: /Revenir à la sélection automatique/i,
      })
      await userEvent.click(backButton)
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
          address: {
            addressAutocomplete: null,
            banId: null,
            city: 'Paris',
            coords: null,
            inseeCode: null,
            isManualEdition: false,
            isVenueAddress: false,
            latitude: '48.8566',
            locationLabel: null,
            longitude: '2.3522',
            offerLocation: 'other',
            postalCode: '75000',
            'search-addressAutocomplete': null,
            street: '10 Rue de Paris',
          },
        },
      })

      const addressSelect = screen.getByRole('combobox', {
        name: /Adresse postale/i,
      }) as HTMLInputElement
      expect(addressSelect).not.toBeDisabled()

      await userEvent.click(
        screen.getByRole('button', {
          name: /Vous ne trouvez pas votre adresse/i,
        })
      )

      const postaleFields = screen.getAllByLabelText(/Adresse postale/i)
      expect(postaleFields.length).toBeGreaterThanOrEqual(2)

      const combobox = screen.getByRole('combobox', {
        name: /Adresse postale/i,
      }) as HTMLInputElement
      expect(combobox).toBeDisabled()

      const manualStreet = postaleFields.find(
        (el) => el.getAttribute('id') === 'street'
      ) as HTMLInputElement | undefined
      expect(manualStreet).toBeDefined()
      expect(manualStreet).not.toBeDisabled()
    })
  })

  describe('disabled state', () => {
    it('should respect isDisabled prop (all interactive elements disabled)', () => {
      renderPhysicalLocationSubform({
        props: { isDisabled: true },
        formDefaults: {
          address: {
            addressAutocomplete: null,
            banId: null,
            city: 'Paris',
            coords: null,
            inseeCode: null,
            isManualEdition: true,
            isVenueAddress: false,
            latitude: '48.8566',
            locationLabel: null,
            longitude: '2.3522',
            offerLocation: 'other',
            postalCode: '75000',
            'search-addressAutocomplete': null,
            street: '10 Rue de Paris',
          },
        },
      })

      expect(
        screen.getByRole('radiogroup', {
          name: 'Il s’agit de l’adresse à laquelle les jeunes devront se présenter.',
        })
      ).toHaveAttribute('aria-disabled', 'true')

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
  })
})
