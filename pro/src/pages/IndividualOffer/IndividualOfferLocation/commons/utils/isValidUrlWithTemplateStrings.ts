import { string } from 'yup'

/**
 * @description
 * This validation has to support template strings in URLs to interpolate these values:
 * - `{email}`: Beneficiary email
 * - `{offerId}`: Offer ID
 * - `{token}`: Offer token ("contremarque")
 *
 * @example `https://example.org/?email={email}&offerID={offerId}&token={token}`
 */
export function isValidUrlWithTemplateStrings(url: string): boolean {
  if (!url.trim()) {
    return false
  }

  // Replace with 'x' instead of removing to preserve URL structure
  // e.g. "https://example.com/{id}/details" -> "https://example.com/x/details" (valid)
  // vs removing: "https://example.com//details" (invalid double slash)
  const urlWithoutTemplates = url.replaceAll(/\{\w+\}/g, 'x')

  return string().url().isValidSync(urlWithoutTemplates)
}
