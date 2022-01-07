import { fireEvent, screen, waitFor } from '@testing-library/react'

import { queryField } from 'ui-kit/form/__tests-utils__'

import {
  CATEGORY_LABEL,
  OFFERER_LABEL,
  SUBCATEGORY_LABEL,
  VENUE_LABEL,
} from '../constants/labels'

export const getCategoriesSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(CATEGORY_LABEL) as HTMLSelectElement

export const getSubcategoriesSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(SUBCATEGORY_LABEL) as HTMLSelectElement

export const getEligibilityBanner = (): HTMLElement =>
  screen.queryByText(
    'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.',
    {
      exact: false,
    }
  ) as HTMLElement

export const getOffererSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(OFFERER_LABEL) as HTMLSelectElement

export const getVenueSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(VENUE_LABEL) as HTMLSelectElement

export const selectOffererAndVenue = async (): Promise<void> => {
  const offererSelect = getOffererSelect()
  fireEvent.change(offererSelect, { target: { value: 'OFFERER_ID' } })
  await waitFor(() => {
    const venueSelect = getVenueSelect()
    fireEvent.change(venueSelect, { target: { value: 'VENUE_ID' } })
  })
}

export const queryElement = {
  OffererSelect: () => queryField<HTMLSelectElement>(OFFERER_LABEL),
  VenueSelect: () => queryField<HTMLSelectElement>(VENUE_LABEL),
  CategorySelect: () => queryField<HTMLSelectElement>(CATEGORY_LABEL),
  SubCategorySelect: () => queryField<HTMLSelectElement>(SUBCATEGORY_LABEL),
}
