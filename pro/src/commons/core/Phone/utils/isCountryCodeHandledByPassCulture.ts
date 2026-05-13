import {
  type PassCultureHandledCountryCode,
  PC_HANDLED_PHONE_COUNTRY_CODES,
  type PlusString,
} from '@/commons/core/Phone/constants'

/**
 * Checks if the given country code is handled by Pass Culture.
 *
 * @param countryCode - The country code to check (must be a string starting with '+').
 * @returns True if the country code is handled by Pass Culture, otherwise false.
 *
 * @example
 * isCountryCodeHandledByPassCulture('+33') // true
 * isCountryCodeHandledByPassCulture('+590') // true
 * isCountryCodeHandledByPassCulture('+444') // false
 */
export const isCountryCodeHandledByPassCulture = (
  countryCode: PlusString
): countryCode is PassCultureHandledCountryCode => {
  // @ts-expect-error: We know that `countryCode` may not be in the array, that's the point of this test …
  return PC_HANDLED_PHONE_COUNTRY_CODES.includes(countryCode)
}
