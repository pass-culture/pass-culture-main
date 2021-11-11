import { httpParameters } from './getInit'
import { getPayload } from './getPayload'
import { errorTimeoutStatusCode } from './status'

export async function fetchData(url, config = {}) {
  const { fetchTimeout } = config

  const fetchConfig = httpParameters(config)
  const fetchPromise = fetch(url, fetchConfig)

  let result
  if (fetchTimeout) {
    const timeoutPromise = new Promise(resolve =>
      setTimeout(
        () => resolve(new Response(null, { status: errorTimeoutStatusCode })),
        fetchTimeout
      )
    )
    result = await Promise.race([timeoutPromise, fetchPromise])
  } else {
    result = await fetchPromise
  }

  const payload = await getPayload(result, fetchConfig)

  return payload
}
