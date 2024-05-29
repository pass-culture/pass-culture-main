import { screen, waitFor } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  ReimbursementFields,
  ReimbursementFieldsProps,
} from '../ReimbursementFields'

const renderReimbursementFields = async (props: ReimbursementFieldsProps) => {
  const rtlReturn = renderWithProviders(
    <Formik onSubmit={() => {}} initialValues={{}}>
      {({ handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          <ReimbursementFields {...props} />
        </Form>
      )}
    </Formik>
  )

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}

describe('ReimbursementFields', () => {
  const venue = {
    ...defaultGetVenue,
    id: 1,
    name: 'fake venue name',
  }
  const otherVenue = {
    id: 2,
    name: 'Offerer Venue',
  } as GetOffererVenueResponseModel
  const offerer = {
    id: 2,
    name: 'fake offerer name',
    managedVenues: [otherVenue],
    hasAvailablePricingPoints: true,
  } as GetOffererResponseModel

  let props: ReimbursementFieldsProps
  beforeEach(() => {
    props = { venue, offerer }
  })

  it('should display banner if offerer has no pricing point and venue has no siret', async () => {
    const offererWithoutPricingPoint = {
      ...offerer,
      hasAvailablePricingPoints: false,
    }
    props.offerer = offererWithoutPricingPoint

    await renderReimbursementFields(props)

    expect(screen.queryByText('Créer un lieu avec SIRET')).toBeInTheDocument()
  })

  it('should not display pricing point section venue has siret', async () => {
    const venueWithSiret = {
      ...venue,
      siret: '00000000012345',
    }
    props.venue = venueWithSiret

    await renderReimbursementFields(props)

    expect(
      screen.queryByText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      )
    ).not.toBeInTheDocument()
  })

  it('should display pricing point section when venue has no siret', async () => {
    const venueWithoutSiret = {
      ...venue,
      siret: '',
    }

    props.venue = venueWithoutSiret

    await renderReimbursementFields(props)

    expect(
      screen.getByText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      )
    ).toBeInTheDocument()
  })
})
