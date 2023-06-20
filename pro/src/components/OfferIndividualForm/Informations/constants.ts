import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from 'components/OfferIndividualForm/Categories/constants'

export const INFORMATIONS_DEFAULT_VALUES = {
  name: '',
  description: '',
  author: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['author'],
  ean: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['ean'],
  performer: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['performer'],
  speaker: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['speaker'],
  stageDirector: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['stageDirector'],
  visa: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['visa'],
  durationMinutes: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['durationMinutes'],
}
