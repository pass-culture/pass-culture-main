import { screen, waitFor } from '@testing-library/react'
import { Form, Formik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { Venue } from 'core/Venue/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import ReimbursementFields, {
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

vi.mock('apiClient/api', () => ({
  api: {
    getAvailableReimbursementPoints: vi.fn(),
  },
}))

describe('ReimbursementFields', () => {
  const venue = {
    id: 1,
    name: 'fake venue name',
  } as Venue
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
    props = { venue, offerer, readOnly: false }
    vi.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])
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
      screen.queryByText('Barème de remboursement')
    ).not.toBeInTheDocument()
  })

  it('should display pricing point section when venue has no siret', async () => {
    const venueWithoutSiret = {
      ...venue,
      siret: '',
    }
    props.venue = venueWithoutSiret

    await renderReimbursementFields(props)

    expect(screen.queryByText('Barème de remboursement')).toBeInTheDocument()
  })
})
