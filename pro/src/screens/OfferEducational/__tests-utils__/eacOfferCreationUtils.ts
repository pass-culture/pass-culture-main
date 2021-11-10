import { screen } from '@testing-library/react'

import { CATEGORY_LABEL, SUBCATEGORY_LABEL } from 'screens/OfferEducational/constants/labels'

export const getCategoriesSelect = (): HTMLSelectElement => 
    screen.getByLabelText(CATEGORY_LABEL) as HTMLSelectElement

export const getSubcategoriesSelect = (): HTMLSelectElement =>
    screen.getByLabelText(SUBCATEGORY_LABEL) as HTMLSelectElement
