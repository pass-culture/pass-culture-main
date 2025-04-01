import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormLocation, FormLocationProps } from '../FormLocation'

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
  let props: FormLocationProps
  let venues: VenueListItemResponseModel[]
  let initialValues: Pick<OfferEducationalFormValues, 'location' | 'venueId'>

  let address = {
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

  beforeEach(() => {
    venues = [venueListItemFactory({ id: 1, address })]

    props = {
      venues,
      disableForm: false,
    }

    initialValues = {
      venueId: '1',
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
  })

  it('should render the location form with title', () => {
    renderFormLocation(props, initialValues)

    expect(screen.getByText('Où se déroule votre offre ?')).toBeInTheDocument()
  })

  it('should display the address option', () => {
    renderFormLocation(props, initialValues)

    expect(screen.getByText('À une adresse précise')).toBeInTheDocument()
  })

  it('should display the selected venue address when venue is selected', async () => {
    renderFormLocation(props, initialValues)

    const addressText = 'Venue 1 - 1 Rue de Paris 75001 Paris'
    expect(await screen.findByText(addressText)).toBeInTheDocument()
  })

  it('should disable the form when disableForm prop is true', () => {
    renderFormLocation({ ...props, disableForm: true }, initialValues)

    // Vérifie que le radio button est désactivé
    const radioInput = screen.getByLabelText('À une adresse précise')
    expect(radioInput).toBeDisabled()
  })
})
