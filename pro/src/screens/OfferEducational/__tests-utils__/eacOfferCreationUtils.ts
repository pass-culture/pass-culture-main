import { screen } from '@testing-library/react'

import {
  CATEGORY_LABEL,
  OFFERER_LABEL,
  SUBCATEGORY_LABEL,
} from 'screens/OfferEducational/constants/labels'

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
