import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { axe } from 'vitest-axe'

import type { AdresseData } from '@/apiClient/adresse/types'
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
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import type { LocationFormValues } from '../../commons/types'
import {
  PhysicalLocationSubform,
  type PhysicalLocationSubformProps,
} from './PhysicalLocationSubform'

const LABELS = {
  locationLabel: /Intitulé de la localisation/,
  addressAutocomplete: /Adresse postale/,
  manuallySetAddressButton: /Vous ne trouvez pas votre adresse ?/,
  automaticallySetAddressButton: /Revenir à la sélection automatique/,
  streetLabel: /Adresse postale/,
}

const MOCK: {
  venueAddress: VenueListItemResponseModel
  addressOptions: AdresseData[]
} = {
  venueAddress: makeVenueListItem({
    id: 1,
    address: {
      id: 1,
      id_oa: 1,
      city: 'Paris',
      isManualEdition: false,
      label: '1 Rue de Paris 75001 Paris',
      postalCode: '75001',
      street: '1 Rue de Paris',
      latitude: 48.87004,
      longitude: 2.3785,
    },
  }),
  addressOptions: [
    {
      address: "17 Rue d'Abbeville",
      city: 'Amiens',
      id: '80021_0050_00017',
      latitude: 49.905915,
      longitude: 2.270522,
      label: "17 Rue d'Abbeville 80000 Amiens",
      postalCode: '80000',
      inseeCode: '80021',
    },
    {
      address: "17 Rue d'Entraigues",
      city: 'Tours',
      id: '37261_1680_00017',
      latitude: 47.388071,
      longitude: 0.688431,
      label: "17 Rue d'Entraigues 37000 Tours",
      postalCode: '37000',
      inseeCode: '37261',
    },
  ],
}

const getDataFromAddressMock = vi.hoisted(() => vi.fn())
vi.mock('@/apiClient/api', () => ({
  getDataFromAddress: getDataFromAddressMock,
}))

const renderPhysicalLocationSubform = (
  {
    props,
    contextValue,
    formValues,
    options,
  }: {
    props?: Partial<PhysicalLocationSubformProps>
    contextValue?: Partial<IndividualOfferContextValues>
    formValues?: Partial<LocationFormValues>
    options?: RenderWithProvidersOptions
  } = {
    props: {},
    contextValue: {},
    formValues: {},
    options: {},
  }
) => {
  const finalProps: PhysicalLocationSubformProps = {
    venue: MOCK.venueAddress,
    isDisabled: false,
    ...props,
  }

  const finalFormValues: LocationFormValues = {
    addressAutocomplete: null,
    banId: null,
    city: null,
    coords: null,
    inseeCode: null,
    isManualEdition: false,
    latitude: null,
    locationLabel: null,
    longitude: null,
    offerLocation: 'venueAddress',
    postalCode: null,
    'search-addressAutocomplete': null,
    street: null,
    url: null,

    ...formValues,
  }

  const finalContextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...contextValue,
  }

  const finalOptions: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...options,
  }

  const PhysicalLocationSubformWrapper = () => {
    const form = useForm<LocationFormValues>({
      defaultValues: finalFormValues,
    })

    return (
      <FormProvider {...form}>
        <PhysicalLocationSubform {...finalProps} />
      </FormProvider>
    )
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={finalContextValue}>
      <PhysicalLocationSubformWrapper />
    </IndividualOfferContext.Provider>,
    finalOptions
  )
}

describe('<PhysicalLocationSubform />', () => {
  it('should render (without accessibility violations)', async () => {
    const { container } = renderPhysicalLocationSubform()

    expect(container).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a radio group with "venue address" and "other address" options', () => {
    renderPhysicalLocationSubform()

    expect(
      screen.getByRole('radio', {
        name: new RegExp(MOCK.venueAddress.address?.label as string),
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', {
        name: 'À une autre adresse',
      })
    ).toBeInTheDocument()
  })

  describe('when the "other address" option is selected', () => {
    it('should render search address fields (without accessibility violations)', async () => {
      const { container } = renderPhysicalLocationSubform({
        formValues: {
          offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
        },
      })

      expect(
        screen.getByRole('combobox', { name: LABELS.addressAutocomplete })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', {
          name: LABELS.manuallySetAddressButton,
        })
      ).toBeInTheDocument()
      expect(await axe(container)).toHaveNoViolations()
    })

    describe('when the "manually set address" button is clicked', () => {
      it('shows manual address fields and can toggle back (without accessibility violations)', async () => {
        const { container } = renderPhysicalLocationSubform({
          formValues: {
            offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
          },
        })

        const manuallySetAddressButton = screen.getByRole('button', {
          name: LABELS.manuallySetAddressButton,
        })

        await userEvent.click(manuallySetAddressButton)

        expect(
          screen.getByRole('textbox', { name: LABELS.streetLabel })
        ).toBeInTheDocument()
        expect(
          screen.getByRole('button', {
            name: LABELS.automaticallySetAddressButton,
          })
        ).toBeInTheDocument()

        await userEvent.click(
          screen.getByRole('button', {
            name: LABELS.automaticallySetAddressButton,
          })
        )
        expect(
          screen.queryByRole('textbox', { name: LABELS.streetLabel })
        ).not.toBeInTheDocument()

        expect(await axe(container)).toHaveNoViolations()
      })
    })
  })

  it('disables inputs when isDisabled=true', () => {
    renderPhysicalLocationSubform({ props: { isDisabled: true } })

    expect(
      screen.getByRole('radiogroup', {
        name: 'Il s’agit de l’adresse à laquelle les jeunes devront se présenter.',
      })
    ).toHaveAttribute('aria-disabled', 'true')

    // Switch to other address to check button disabled state
    expect(
      screen.getByRole('radio', {
        name: new RegExp(MOCK.venueAddress.address?.label as string),
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'À une autre adresse' })
    ).toBeInTheDocument()
  })
})
