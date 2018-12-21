import get from 'lodash.get'
import queryString from 'query-string'

export const canSubmitForm = formProps => {
  const {
    // https://github.com/final-form/final-form#formstate
    dirtySinceLastSubmit,
    hasSubmitErrors,
    hasValidationErrors,
    pristine,
  } = formProps
  const canSubmit =
    (!pristine && !hasSubmitErrors && !hasValidationErrors) ||
    (!hasValidationErrors && hasSubmitErrors && dirtySinceLastSubmit)
  return canSubmit
}

export const getQueryStringEmail = location => {
  const searchQuery = get(location, 'search') || undefined
  if (!searchQuery) return undefined
  const parsed = queryString.parse(searchQuery)
  const email = get(parsed, 'email') || undefined
  return email
}

export const getURLTokenParam = match => {
  const token = get(match, 'params.token') || undefined
  return token
}
