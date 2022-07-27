import { screen } from '@testing-library/react'

import { QueryFieldResponse, queryField } from 'ui-kit/form/__tests-utils__'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL,
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  OFFERER_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
  VENUE_LABEL,
} from '../constants/labels'

export const elements = {
  queryOffererSelect: (): Promise<QueryFieldResponse<HTMLSelectElement>> =>
    queryField<HTMLSelectElement>(OFFERER_LABEL),

  queryVenueSelect: (): Promise<QueryFieldResponse<HTMLSelectElement>> =>
    queryField<HTMLSelectElement>(VENUE_LABEL),

  findOfferTypeTitle: (): Promise<HTMLElement> =>
    screen.findByRole('heading', {
      name: 'Type d’offre',
    }),

  queryOfferTypeTitle: (): HTMLElement | null =>
    screen.queryByRole('heading', {
      name: 'Type d’offre',
    }),

  queryCategorySelect: (): Promise<QueryFieldResponse<HTMLSelectElement>> =>
    queryField<HTMLSelectElement>(CATEGORY_LABEL),

  querySubcategorySelect: (): Promise<QueryFieldResponse<HTMLSelectElement>> =>
    queryField<HTMLSelectElement>(SUBCATEGORY_LABEL),

  queryTitleInput: (): Promise<QueryFieldResponse<HTMLInputElement>> =>
    queryField<HTMLInputElement>(TITLE_LABEL),

  queryDescriptionTextArea: (): Promise<
    QueryFieldResponse<HTMLTextAreaElement>
  > => queryField<HTMLTextAreaElement>(DESCRIPTION_LABEL),

  queryDurationInput: (): Promise<QueryFieldResponse<HTMLInputElement>> =>
    queryField<HTMLInputElement>(DURATION_LABEL),

  queryOfferVenueRadioButtons: (): {
    offererVenueRadio: Promise<QueryFieldResponse<HTMLInputElement>>
    schoolRadio: Promise<QueryFieldResponse<HTMLInputElement>>
    otherRadio: Promise<QueryFieldResponse<HTMLInputElement>>
  } => ({
    offererVenueRadio: queryField<HTMLInputElement>(
      EVENT_ADDRESS_OFFERER_LABEL
    ),
    schoolRadio: queryField<HTMLInputElement>(EVENT_ADDRESS_SCHOOL_LABEL),
    otherRadio: queryField<HTMLInputElement>(EVENT_ADDRESS_OTHER_LABEL),
  }),

  queryOfferVenueSelect: (): Promise<QueryFieldResponse<HTMLSelectElement>> =>
    queryField<HTMLSelectElement>(EVENT_ADDRESS_OFFERER_VENUE_SELECT_LABEL),

  queryOfferVenueAddressDisplay: (): HTMLElement | null =>
    screen.queryByText('Venue name', { exact: false, selector: 'p' }),

  queryOfferVenueTextArea: (): Promise<
    QueryFieldResponse<HTMLTextAreaElement>
  > => queryField<HTMLTextAreaElement>(EVENT_ADDRESS_OTHER_ADDRESS_LABEL),
}
