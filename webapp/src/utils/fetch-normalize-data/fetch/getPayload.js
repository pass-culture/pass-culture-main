import {
  errorTimeoutStatusCode,
  successStatusCodesWithDataOrDatum,
  successStatusCodesWithoutDataAndDatum,
  errorServiceUnavailableStatusCode,
} from './status'

export const GLOBAL_RESULT_ERROR = 'Result returned by the server is not at the good json format'

export async function getPayload(result, config) {
  const globalResultError = config.globalResultError || GLOBAL_RESULT_ERROR
  const { ok, status } = result
  const headers = {}
  result.headers.forEach((value, key) => {
    headers[key] = value
  })

  const payload = { headers, ok, status }

  if (errorTimeoutStatusCode === status || errorServiceUnavailableStatusCode === status) {
    payload.errors = [
      {
        global: [globalResultError],
      },
      {
        timeout: [result.statusText],
      },
    ]
    return payload
  }

  if (successStatusCodesWithDataOrDatum.includes(status)) {
    if (!result.json) {
      payload.errors = [
        {
          global: [globalResultError],
        },
      ]
      return payload
    }

    const dataOrDatum = await result.json()
    if (Array.isArray(dataOrDatum)) {
      payload.data = dataOrDatum
    } else if (typeof dataOrDatum === 'object') {
      payload.datum = dataOrDatum
    }

    return payload
  }

  if (successStatusCodesWithoutDataAndDatum.includes(status)) {
    return payload
  }

  if (!result.json) {
    payload.errors = [
      {
        global: [globalResultError],
      },
    ]
    return payload
  }

  payload.errors = await result.json()
  return payload
}
