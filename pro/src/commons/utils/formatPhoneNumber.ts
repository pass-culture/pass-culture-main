import parsePhoneNumberFromString, {
  type NumberFormat,
} from 'libphonenumber-js/max'

/**
 * Formats a French phone number using libphonenumber-js.
 *
 * @param value - The phone number to format (string, null, or undefined).
 * @param format - The desired phone number format (defaults to 'INTERNATIONAL').
 * @returns The formatted phone number, or an empty string if no value is provided, or the input if formatting fails.
 *
 * @example
 * formatPhoneNumber('+33612345678') // '+33 6 12 34 56 78'
 * formatPhoneNumber('+33612345678', 'NATIONAL') // '06 12 34 56 78'
 *
 * formatPhoneNumber('+262692345678') // '+262 692 34 56 78'
 * formatPhoneNumber('+262692345678', 'NATIONAL') // '0692 34 56 78'
 */
export const formatPhoneNumber = (
  value: string | null | undefined,
  format: NumberFormat = 'INTERNATIONAL'
): string => {
  if (!value) {
    return ''
  }

  try {
    const parsedPhone = parsePhoneNumberFromString(value, 'FR')
    return parsedPhone?.format(format) ?? value
  } catch {
    return value
  }
}
