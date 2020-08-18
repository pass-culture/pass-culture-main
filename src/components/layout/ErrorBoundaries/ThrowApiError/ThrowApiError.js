import { PropTypes } from 'prop-types'

import { ApiError } from './ApiError'

export const ThrowApiError = ({ httpErrorCode }) => {
  throw new ApiError(httpErrorCode)
}

ThrowApiError.propTypes = {
  httpErrorCode: PropTypes.number.isRequired,
}
