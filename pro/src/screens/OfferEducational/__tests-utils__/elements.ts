import { screen } from '@testing-library/react'

import { queryField, QueryFieldResponse } from 'ui-kit/form/__tests-utils__'

import {
  OFFERER_LABEL,
  VENUE_LABEL,
  CATEGORY_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
} from '../constants/labels'

export const elements = {
  queryOffererSelect: (): QueryFieldResponse<HTMLSelectElement> =>
    queryField<HTMLSelectElement>(OFFERER_LABEL),

  queryVenueSelect: (): QueryFieldResponse<HTMLSelectElement> =>
    queryField<HTMLSelectElement>(VENUE_LABEL),

  findOfferTypeTitle: (): Promise<HTMLElement> =>
    screen.findByRole('heading', {
      name: 'Type d’offre',
    }),

  queryOfferTypeTitle: (): HTMLElement | null =>
    screen.queryByRole('heading', {
      name: 'Type d’offre',
    }),

  queryCategorySelect: (): QueryFieldResponse<HTMLSelectElement> =>
    queryField<HTMLSelectElement>(CATEGORY_LABEL),

  querySubcategorySelect: (): QueryFieldResponse<HTMLSelectElement> =>
    queryField<HTMLSelectElement>(SUBCATEGORY_LABEL),

  queryTitleInput: (): QueryFieldResponse<HTMLInputElement> =>
    queryField<HTMLInputElement>(TITLE_LABEL),

  queryDescriptionTextArea: (): QueryFieldResponse<HTMLTextAreaElement> =>
    queryField<HTMLTextAreaElement>(DESCRIPTION_LABEL),

  queryDurationInput: (): QueryFieldResponse<HTMLInputElement> =>
    queryField<HTMLInputElement>(DURATION_LABEL),
}
