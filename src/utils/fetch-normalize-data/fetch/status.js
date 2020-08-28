export const errorTimeoutStatusCode = 504

export const successStatusCodesWithDataOrDatum = [
  200,
  201,
  202,
  203,
  205,
  206,
  207,
  208,
  210,
  226,
]

export const successStatusCodesWithoutDataAndDatum = [
  204,
]

export const isSuccessStatus = status => {
  return (
    successStatusCodesWithDataOrDatum.includes(status) ||
    successStatusCodesWithoutDataAndDatum.includes(status)
  )
}

export const isTimeoutStatus = status => {
  return errorTimeoutStatusCode === status
}
