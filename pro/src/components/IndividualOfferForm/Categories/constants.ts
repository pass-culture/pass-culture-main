export const SUBCATEGORIES_FIELDS_DEFAULT_VALUES = {
  gtl_id: '',
  musicType: '',
  musicSubType: '',
  showType: '',
  showSubType: '',
  author: '',
  ean: '',
  performer: '',
  speaker: '',
  stageDirector: '',
  visa: '',
  durationMinutes: '',
  withdrawalType: undefined,
  withdrawalDelay: undefined,
}

export const CATEGORIES_DEFAULT_VALUES = {
  subCategoryFields: [],
  categoryId: '',
  subcategoryId: '',
  isEvent: false,
  ...SUBCATEGORIES_FIELDS_DEFAULT_VALUES,
}
