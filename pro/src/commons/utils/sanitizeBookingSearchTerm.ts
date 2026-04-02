const REMOVE_ACCENTS_REGEX = /[\u0300-\u036f]/g

export const sanitizeBookingSearchTerm = (input: string): string =>
  input.normalize('NFD').replace(REMOVE_ACCENTS_REGEX, '').trim().toLowerCase()
