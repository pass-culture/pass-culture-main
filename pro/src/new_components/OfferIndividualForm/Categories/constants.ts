export const SUBCATEGORIES_FIELDS_DEFAULT_VALUES = {
  musicType: '',
  musicSubType: '',
  showType: '',
  showSubType: '',
  author: '',
  isbn: '',
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
