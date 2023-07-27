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

const renderReimbursementFields = async (
  props: ReimbursementFieldsProps,
  storeOverrides: any
) => {
  const rtlReturn = renderWithProviders(
    <Formik onSubmit={() => {}} initialValues={{}}>
      {({ handleSubmit }) => (
        <Form onSubmit={handleSubmit}>
          <ReimbursementFields {...props} />
        </Form>
      )}
    </Formik>,
    { storeOverrides }
  )

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}

jest.mock('apiClient/api', () => ({
  api: {
    getAvailableReimbursementPoints: vi.fn(),
  },
}))

describe('src | Venue | ReimbursementFields', () => {
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

  const mockLogEvent = vi.fn()
  let props: ReimbursementFieldsProps
  let store: any
  beforeEach(() => {
    props = { venue, offerer, readOnly: false }
    store = {
      app: { logEvent: mockLogEvent },
    }
    vi.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])
  })

  it('should display banner if offerer has no pricing point and venue has no siret', async () => {
    // Given
    const offererWithoutPricingPoint = {
      ...offerer,
      hasAvailablePricingPoints: false,
    }
    props.offerer = offererWithoutPricingPoint

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(screen.queryByText('Créer un lieu avec SIRET')).toBeInTheDocument()
  })

  it('should not display pricing point section venue has siret', async () => {
    // Given
    const venueWithSiret = {
      ...venue,
      siret: '00000000012345',
    }
    props.venue = venueWithSiret

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(
      screen.queryByText('Barème de remboursement')
    ).not.toBeInTheDocument()
  })

  it('should display pricing point section when venue has no siret', async () => {
    // Given
    const venueWithoutSiret = {
      ...venue,
      siret: '',
    }
    props.venue = venueWithoutSiret

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(screen.queryByText('Barème de remboursement')).toBeInTheDocument()
  })
})
