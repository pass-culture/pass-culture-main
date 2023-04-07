// FIXME (mageoffray, 2023-03-24)
// This is a temporary module to remove humanizedId.
// For 6 months (until around 2023-10-01) we should redirect
// urls with humanized params to url wih non human parameters

import { decode } from 'hi-base32'
import type { Location } from 'react-router-dom'

import { parse } from 'utils/query-string'

const paramsToRedirect = ['offererId', 'offerId', 'venueId']
const queryParamsToRedirect = ['structure', 'lieu', 'offerVenueId']

export const dehumanizeId = (humanId: string) => {
  try {
    return byteArrayToInt(
      decode.asBytes(humanId.replace(/8/g, 'O').replace(/9/g, 'I'))
    )
  } catch (e) {
    /* istanbul ignore next */
    return null
  }
}

const byteArrayToInt = (bytes: number[]) =>
  bytes.reduce(
    (result, byte, index) =>
      result + byte * Math.pow(256, bytes.length - 1 - index),
    0
  )

const dehumanizeString = (
  paramObject: Record<string, string | undefined>,
  redirectionParams: string[],
  stringToDehumanize: string
): string => {
  const dehumanizedIdRegex = new RegExp(/^\d+$/)
  let dehumanizedString = stringToDehumanize
  for (const [key, value] of Object.entries(paramObject)) {
    if (
      redirectionParams.includes(key) &&
      value &&
      !dehumanizedIdRegex.test(value)
    ) {
      const dehumanizedId = dehumanizeId(value)
      if (dehumanizedId) {
        dehumanizedString = dehumanizedString.replace(
          value,
          dehumanizedId.toString()
        )
      }
    }
  }
  return dehumanizedString
}

export const dehumanizedRoute = (
  location: Location,
  matches: {
    id: string
    pathname: string
    params: Record<string, string | undefined>
    data: unknown
    handle: unknown
  }[]
) => {
  const newLoc = dehumanizeString(
    matches[0].params,
    paramsToRedirect,
    location.pathname
  )

  const newQueryString = dehumanizeString(
    parse(location.search),
    queryParamsToRedirect,
    location.search
  )

  return newLoc + newQueryString
}
