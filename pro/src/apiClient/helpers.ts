import type { ApiError } from './v1'

export const serializeApiErrors = (
  errors: Record<string, string[]>,
  apiFieldsMap: Record<string, string> = {},
  apiArrayFieldsMap: Record<string, string> = {}
): Record<string, string[] | undefined> => {
  Object.entries(apiFieldsMap).forEach(([key, value]) => {
    if (errors[key]) {
      errors[value] = errors[key]
      delete errors[key]
    }
  })

  //  Arrays must be serialized in a different way. The error from the api for a list of bookingEmails will be
  //  {bookingEmails.3: ['Invalid email'], bookingEmails.6: ['Invalid email']}
  //  While the formik form expects {notificationEmails: ['', '', '', 'Invalid email', '', '', 'Invalid email']}
  Object.entries(apiArrayFieldsMap).forEach(([key, value]) => {
    const errorKeys = Object.keys(errors).filter((errKey) =>
      errKey.startsWith(`${key}.`)
    )
    const errorIndexes = errorKeys
      .map((err) => Number(err.split(`${key}.`)[1]))
      .filter((num) => !Number.isNaN(num))

    const errorValues = []
    //  Recontruct an array up to the biggest index with an error in the list of errors on that field
    for (let i = 0; i <= Math.max(...errorIndexes); i++) {
      errorValues.push(
        errorKeys.includes(`${key}.${i}`) ? errors[`${key}.${i}`][0] : ''
      )
      delete errors[`${key}.${i}`]
    }
    errors[value] = errorValues
  })
  return errors
}

type ErrorAdage = {
  statusCode: number
  body: {
    code: string
  }
}

// TODO remove this function because it is use at only one place
// biome-ignore lint/suspicious/noExplicitAny: Generic error.
export const hasErrorCode = (error: any): error is ErrorAdage =>
  typeof error?.body?.code === 'string'

export const getErrorCode = (error: ApiError): string => {
  return error.body.code
}

export const isError = (error: unknown): error is Error =>
  typeof error === 'object' && error !== null && 'message' in error

export const isErrorAPIError = (error: unknown): error is ApiError =>
  isError(error) && 'name' in error && error.name === 'ApiError'

export const getError = (error: ApiError) => {
  return error.body
}

export const getHumanReadableApiError = (
  error: unknown,
  defaultMessage = 'Une erreur s’est produite, veuillez réessayer'
) => {
  if (!isErrorAPIError(error)) {
    return defaultMessage
  }

  const { body } = error

  if (Array.isArray(body) && body.length > 0) {
    return body.map((bodyValue) => Object.values(bodyValue).join(' ')).join(' ')
  }

  if (body instanceof Object && Object.keys(body).length > 0) {
    return Object.values(body)
      .map((bodyValue) =>
        Array.isArray(bodyValue) ? bodyValue.join(' ') : bodyValue
      )
      .join(' ')
  }

  return defaultMessage
}

// TODO: find a way to test this by mocking ReadableStream
// in fetch response
/* istanbul ignore next */
export const getFileFromURL = async (
  url: string,
  name = 'image.jpg'
): Promise<File> => {
  const response = await fetch(url)
  const blob = await response.blob()
  return new File([blob], name, { type: blob.type })
}

export const HTTP_STATUS = {
  NO_CONTENT: 204,
  FORBIDDEN: 403,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
  TOO_MANY_REQUESTS: 429,
  GONE: 410,
  NOT_FOUND: 404,
}
