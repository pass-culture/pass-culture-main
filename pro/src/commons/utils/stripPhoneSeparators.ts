/**
 * Removes spaces, dots, and hyphens from the given phone number string.
 *
 * @param value - The phone number string to clean.
 * @returns The phone number string without spaces, dots or hyphens.
 *
 * @example
 * stripPhoneSeparators('06 12 34 56 78') // '612345678'
 * stripPhoneSeparators('06-12-34-56-78') // '612345678'
 * stripPhoneSeparators('06.12.34.56.78') // '612345678'
 * stripPhoneSeparators('6 12 34 56 78') // '612345678'
 */
export const stripPhoneSeparators = (value: string | null | undefined) =>
  value?.replaceAll(/(\s|\.|-)/g, '') ?? ''
