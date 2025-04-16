import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'

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

const renderFormLocation = (
  props: FormLocationProps,
  initialValues: Pick<OfferEducationalFormValues, 'location' | 'venueId'>
) => {
  renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={() => {}}>
      <FormLocation {...props} />
    </Formik>
  )
}

describe('FormLocation', () => {
  const address = {
    banId: null,
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

  const initialValues: Pick<
    OfferEducationalFormValues,
    | 'location'
    | 'venueId'
    | 'search-addressAutocomplete'
    | 'addressAutocomplete'
  > = {
    venueId: '1',
    'search-addressAutocomplete': '',
    addressAutocomplete: '',
    location: {
      locationType: CollectiveLocationType.ADDRESS,
      id_oa: '889',
      address: {
        city: 'Paris',
        isVenueAddress: true,
        latitude: 48.87004,
        longitude: 2.3785,
        postalCode: '75001',
        street: '1 Rue de Paris',
      },
    },
  }

  beforeEach(() => {
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue(mockAdressData)
  })

  it('should render the location form with title', () => {
    renderFormLocation(props, initialValues)

    expect(screen.getByText('Où se déroule votre offre ?')).toBeInTheDocument()
  })

  it('should display the address option', () => {
    renderFormLocation(props, initialValues)

    expect(screen.getByText('À une adresse précise')).toBeInTheDocument()
  })

  it('should display the selected venue address by default', async () => {
    renderFormLocation(props, initialValues)

    const addressText = 'Venue 1 - 1 Rue de Paris 75001 Paris'
    expect(await screen.findByText(addressText)).toBeInTheDocument()
  })

  it('should update address fields when an address is selected from autocomplete', async () => {
    renderFormLocation(props, initialValues)

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
  })

  it('should disable the form when disableForm prop is true', () => {
    renderFormLocation({ ...props, disableForm: true }, initialValues)

    const radioInput = screen.getByLabelText('À une adresse précise')
    expect(radioInput).toBeDisabled()
  })
})
