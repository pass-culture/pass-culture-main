import { screen } from '@testing-library/react'

import {
  CATEGORY_LABEL,
  SUBCATEGORY_LABEL,
} from 'screens/OfferEducational/constants/labels'

export const getCategoriesSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(CATEGORY_LABEL) as HTMLSelectElement

export const getSubcategoriesSelect = (): HTMLSelectElement =>
  screen.queryByLabelText(SUBCATEGORY_LABEL) as HTMLSelectElement
