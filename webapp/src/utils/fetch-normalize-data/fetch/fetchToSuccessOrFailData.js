import { handleApiError } from './errors/handleApiError'
import { handleServerError } from './errors/handleServerError'
import { handleTimeoutError } from './errors/handleTimeoutError'
import { fetchData } from './fetchData'
import { getConfigWithDefaultValues } from './getConfigWithDefaultValues'
import { getUrlFromConfig } from './getUrlFromConfig'
import { handleApiSuccess } from './handleApiSuccess'
import { isSuccessStatus, isTimeoutStatus } from './status'

export async function fetchToSuccessOrFailData(reducer, configWithoutDefaultValues) {
  const config = getConfigWithDefaultValues(configWithoutDefaultValues)

  const url = getUrlFromConfig(config)

  const fetchDataMethod = config.fetchData || fetchData

  try {
    const payload = await fetchDataMethod(url, config)

    const isSuccess = isSuccessStatus(payload.status)
    if (isSuccess) {
      handleApiSuccess(reducer, payload, config)
      return
    }

    const isTimeout = isTimeoutStatus(payload.status)
    if (isTimeout) {
      handleTimeoutError(reducer, payload, config)
      return
    }

    if (payload.errors) {
      handleApiError(reducer, payload, config)
    }
  } catch (error) {
    handleServerError(reducer, error, config)
  }
}
