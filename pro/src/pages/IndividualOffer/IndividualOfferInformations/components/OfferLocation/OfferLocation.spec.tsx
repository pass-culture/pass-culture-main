import { AdresseData } from 'apiClient/adresse/types'
import { VenueListItemResponseModel } from 'apiClient/v1'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  individualOfferContextValuesFactory,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { UsefulInformationFormValues } from 'pages/IndividualOffer/IndividualOfferInformations/commons/types'
import { FormProvider, useForm } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { OfferLocation, OfferLocationProps } from './OfferLocation'

const LABELS = {
  locationLabel: /Intitulés de la localisation/,
  addressAutocomplete: /Adresse postale/,
  manuallySetAddressButton: /Vous ne trouvez pas votre adresse ?/,
  automaticallySetAddressButton: /Revenir à la sélection automatique/,
  streetLabel: /Adresse postale/,
}

const MOCK: {
  venueAddress: VenueListItemResponseModel
  addressOptions: AdresseData[]
} = {
  venueAddress: venueListItemFactory({
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
vi.mock('apiClient/api', () => ({
  getDataFromAddress: getDataFromAddressMock,
}))

const renderOfferLocation = (
  {
    props,
    contextValue,
    formValues,
    options,
  }: {
    props?: Partial<OfferLocationProps>
    contextValue?: Partial<IndividualOfferContextValues>
    formValues?: Partial<UsefulInformationFormValues>
    options?: RenderWithProvidersOptions
  } = {
    props: {},
    contextValue: {},
    formValues: {},
    options: {},
  }
) => {
  const finalProps: OfferLocationProps = {
    venue: MOCK.venueAddress,
    readOnlyFields: [],
    ...props,
  }

  const finalFormValues: UsefulInformationFormValues = {
    accessibility: {
      audio: false,
      mental: false,
      motor: false,
      visual: false,
      none: true,
    },
    addressAutocomplete: '',
    banId: '',
    bookingContact: '',
    bookingEmail: '',
    city: '',
    coords: '',
    externalTicketOfficeUrl: '',
    inseeCode: '',
    isEvent: false,
    isNational: false,
    latitude: '',
    locationLabel: '',
    longitude: '',
    manuallySetAddress: false,
    offerLocation: 'venueAddress',
    postalCode: '',
    receiveNotificationEmails: false,
    'search-addressAutocomplete': '',
    street: '',
    withdrawalDelay: '',
    withdrawalType: undefined,
    withdrawalDetails: '',
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

  const OfferLocationWrapper = () => {
    const form = useForm<UsefulInformationFormValues>({
      defaultValues: finalFormValues,
    })

    return (
      <FormProvider {...form}>
        <OfferLocation {...finalProps} />
      </FormProvider>
    )
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={finalContextValue}>
      <OfferLocationWrapper />
    </IndividualOfferContext.Provider>,
    finalOptions
  )
}

describe('OfferLocation', () => {
  it('should render (without accessibility violations)', async () => {
    const { container } = renderOfferLocation()

    expect(container).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display a radio group with "venue address" and "other address" options', () => {
    renderOfferLocation()

    expect(
      screen.getByRole('radio', {
        name: new RegExp(MOCK.venueAddress.address?.label as string),
      })
    )
    expect(
      screen.getByRole('radio', {
        name: 'À une autre adresse',
      })
    )
  })

  describe('when the "other address" option is selected', () => {
    it('should render search address fields (without accessibility violations)', async () => {
      const { container } = renderOfferLocation({
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
      it('should display extra / manual address fields (without accessibility violations)', async () => {
        const { container } = renderOfferLocation({
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

        expect(await axe(container)).toHaveNoViolations()
      })
    })
  })
})
