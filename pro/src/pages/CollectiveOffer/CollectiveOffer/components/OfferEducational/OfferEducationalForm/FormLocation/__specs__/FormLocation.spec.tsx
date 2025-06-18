import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import * as apiAdresse from 'apiClient/adresse/apiAdresse'
import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormLocation, FormLocationProps } from '../FormLocation'

const mockAdressData = [
  {
    address: '10 Rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '10 Rue des lilas 69002 Lyon',
    postalCode: '69002',
    inseeCode: '69002',
  },
]

vi.mock('apiClient/adresse', async () => {
  return {
    ...(await vi.importActual('apiClient/adresse/apiAdresse')),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

const initialValues: Pick<
  OfferEducationalFormValues,
  | 'location'
  | 'venueId'
  | 'search-addressAutocomplete'
  | 'addressAutocomplete'
  | 'city'
  | 'latitude'
  | 'longitude'
  | 'postalCode'
  | 'street'
  | 'coords'
  | 'interventionArea'
> = {
  venueId: '1',
  'search-addressAutocomplete': '',
  addressAutocomplete: '',
  city: 'Paris',
  latitude: '48.87004',
  longitude: '2.3785',
  postalCode: '75001',
  street: '1 Rue de Paris',
  coords: '48.87004, 2.3785',
  location: {
    locationType: CollectiveLocationType.ADDRESS,
    address: {
      id_oa: '889',
      isVenueAddress: true,
      isManualEdition: false,
      label: '',
    },
  },
  interventionArea: [],
}

function renderFormLocation(
  props: FormLocationProps,
  initialValues: Pick<
    OfferEducationalFormValues,
    'location' | 'venueId' | 'interventionArea'
  >
) {
  let getValues: () => any

  function FormLocationWrapper() {
    const form = useForm({
      defaultValues: initialValues,
    })

    getValues = form.getValues

    return (
      <FormProvider {...form}>
        <FormLocation {...props} />
      </FormProvider>
    )
  }

  return {
    ...renderWithProviders(<FormLocationWrapper />),
    getValues: () => getValues(),
  }
}

describe('FormLocation', () => {
  const address = {
    banId: '',
    city: 'Paris',
    departmentCode: '75',
    id: 1,
    id_oa: 889,
    inseeCode: null,
    isLinkedToVenue: true,
    isManualEdition: false,
    label: 'Venue 1',
    latitude: 48.87004,
    longitude: 2.3785,
    postalCode: '75001',
    street: '1 Rue de Paris',
  }

  const venues: VenueListItemResponseModel[] = [
    venueListItemFactory({ id: 1, address }),
  ]

  const props: FormLocationProps = {
    venues,
    disableForm: false,
  }

  beforeEach(() => {
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue(mockAdressData)
  })

  it('should render the location form with title', () => {
    renderFormLocation(props, initialValues)

    expect(
      screen.getByText('Où se déroule votre offre ? *')
    ).toBeInTheDocument()
  })

  it('should display the address option', () => {
    renderFormLocation(props, initialValues)

    expect(screen.getByText('À une adresse précise')).toBeInTheDocument()
  })

  it('should update address fields when an address is selected from autocomplete', async () => {
    const { getValues } = renderFormLocation(props, initialValues)

    await userEvent.click(screen.getByText('Autre adresse'))

    const adressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.type(adressInput, '10 rue ')

    const addressSuggestion = await screen.findByText(
      '10 Rue des lilas 69002 Lyon',
      {
        selector: 'span',
      }
    )

    await userEvent.click(addressSuggestion)

    expect(
      await screen.findByText('10 Rue des lilas 69002 Lyon', {
        selector: 'option',
      })
    ).toBeInTheDocument()

    const formValues = getValues()

    expect(formValues.street).toBe('10 Rue des lilas')
    expect(formValues.postalCode).toBe('69002')
    expect(formValues.latitude).toBe('11.1')
    expect(formValues.longitude).toBe('-11.1')
    expect(formValues.coords).toBe('48.87004, 2.3785')
    expect(formValues.banId).toBe('1')
  })

  it('should disable the form when disableForm prop is true', () => {
    renderFormLocation({ ...props, disableForm: true }, initialValues)

    const addressInput = screen.getByLabelText('À une adresse précise')
    const institutionInput = screen.getByLabelText('En établissement scolaire')
    expect(addressInput).toBeDisabled()
    expect(institutionInput).toBeDisabled()
  })

  it('should display the institution option', () => {
    renderFormLocation(props, initialValues)

    expect(
      screen.getByLabelText('En établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should show manual address form when isManualEdition is true', () => {
    renderFormLocation(props, {
      ...initialValues,
      location: {
        ...initialValues.location,
        address: {
          ...initialValues.location?.address,
          id_oa: 'SPECIFIC_ADDRESS',
          isManualEdition: true,
          isVenueAddress: false,
          label: 'mon adresse manuelle',
        },
      },
    })

    const labelInput = screen.getByLabelText('Intitulé de la localisation')

    const addressInput = screen.getByLabelText(/Adresse postale/, {
      selector: '#street',
    })
    const cityInput = screen.getByLabelText(/Ville/)
    const postalCodeInput = screen.getByLabelText(/Code postal/)
    const coordsInput = screen.getByLabelText(/Coordonnées GPS/)

    expect(labelInput).toHaveValue('mon adresse manuelle')
    expect(addressInput).toHaveValue('1 Rue de Paris')
    expect(cityInput).toHaveValue('Paris')
    expect(postalCodeInput).toHaveValue('75001')
    expect(coordsInput).toHaveValue('48.87004, 2.3785')
  })

  it('should disable manual address form when disableForm prop is true', () => {
    renderFormLocation(
      { ...props, disableForm: true },
      {
        ...initialValues,
        location: {
          ...initialValues.location,
          address: {
            ...initialValues.location?.address,
            id_oa: 'SPECIFIC_ADDRESS',
            isManualEdition: true,
          },
        },
      }
    )

    const radioInput = screen.getByLabelText('Autre adresse')
    const addressLabelInput = screen.getByLabelText(
      'Intitulé de la localisation'
    )
    const addressInput = screen.getByLabelText(/Adresse postale/, {
      selector: '#street',
    })
    const cityInput = screen.getByLabelText(/Ville/)
    const postalCodeInput = screen.getByLabelText(/Code postal/)
    const coordsInput = screen.getByLabelText(/Coordonnées GPS/)

    expect(radioInput).toBeDisabled()
    expect(addressLabelInput).toBeDisabled()
    expect(addressInput).toBeDisabled()
    expect(cityInput).toBeDisabled()
    expect(postalCodeInput).toBeDisabled()
    expect(coordsInput).toBeDisabled()
  })

  it('should show manual address form on press "Vous ne trouvez pas votre adresse ?" and empty address fields', async () => {
    renderFormLocation(props, {
      ...initialValues,
      location: {
        ...initialValues.location,
        address: {
          ...initialValues.location?.address,
          id_oa: 'SPECIFIC_ADDRESS',
        },
      },
    })

    const showManualAddressFormButton = screen.getByText(
      'Vous ne trouvez pas votre adresse ?'
    )

    await userEvent.click(showManualAddressFormButton)

    const addressInput = screen.getByLabelText(/Adresse postale/, {
      selector: '#street',
    })
    const cityInput = screen.getByLabelText(/Ville/)
    const postalCodeInput = screen.getByLabelText(/Code postal/)
    const coordsInput = screen.getByLabelText(/Coordonnées GPS/)

    expect(addressInput).toBeInTheDocument()
    expect(cityInput).toBeInTheDocument()
    expect(postalCodeInput).toBeInTheDocument()
    expect(coordsInput).toBeInTheDocument()
  })

  it('should show intervention area multiselect on press school option', async () => {
    renderFormLocation(props, initialValues)

    const schoolRadio = screen.getByLabelText('En établissement scolaire')
    await userEvent.click(schoolRadio)

    const interventionAreaMultiselect = screen.getByLabelText('Département(s)')
    expect(interventionAreaMultiselect).toBeInTheDocument()
  })

  it('should show intervention area multiselect and comment text area on press "à déterminer" option', async () => {
    renderFormLocation(props, initialValues)

    const toBeDefinedRadio = screen.getByLabelText(
      'À déterminer avec l’enseignant'
    )
    await userEvent.click(toBeDefinedRadio)

    const interventionAreaMultiselect = screen.getByLabelText('Département(s)')
    expect(interventionAreaMultiselect).toBeInTheDocument()
    const commentTextArea = screen.getByLabelText('Commentaire')
    expect(commentTextArea).toBeInTheDocument()
  })

  it('should show school radio checked with intervention areas selected when location type is SCHOOL', () => {
    renderFormLocation(props, {
      ...initialValues,
      location: {
        locationType: CollectiveLocationType.SCHOOL,
      },
      interventionArea: ['44'],
    })

    const departmentTag = screen.getByText('44 - Loire-Atlantique')
    expect(departmentTag).toBeInTheDocument()
  })

  it('should show "à déterminer" radio checked with intervention areas selected when location type is TO_BE_DEFINED', () => {
    renderFormLocation(props, {
      ...initialValues,
      location: {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        locationComment: 'quelque part',
      },
      interventionArea: ['44'],
    })

    expect(screen.getByText('44 - Loire-Atlantique')).toBeInTheDocument()

    expect(screen.getByLabelText('Commentaire')).toHaveValue('quelque part')
  })

  it('should set the venue address fields when the type of location is address', async () => {
    renderFormLocation(props, initialValues)

    await userEvent.click(screen.getByLabelText('En établissement scolaire'))

    await userEvent.click(screen.getByText('À une adresse précise'))

    await userEvent.click(screen.getByText('Autre adresse'))

    await userEvent.click(
      screen.getByText('Vous ne trouvez pas votre adresse ?')
    )

    expect(screen.getByLabelText('Ville *')).toHaveValue(
      props.venues.find((v) => v.id === Number(initialValues.venueId))?.address
        ?.city
    )
  })
})
