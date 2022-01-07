import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { queryField } from 'ui-kit/form/__tests-utils__'

import { OFFERER_LABEL, VENUE_LABEL } from '../constants/labels'

export const selectOffererAndVenue = async (): Promise<void> => {
  const offererSelect = queryField<HTMLSelectElement>(OFFERER_LABEL)
  userEvent.selectOptions(
    offererSelect.input as HTMLSelectElement,
    'OFFERER_ID'
  )

  await waitFor(() => {
    const venueSelect = queryField<HTMLSelectElement>(VENUE_LABEL)
    userEvent.selectOptions(venueSelect.input as HTMLSelectElement, 'VENUE_ID')
  })
}
