export function isRequestAction = ({ type }) =>
  /REQUEST_(.*)/.test(type)

export function isSuccessAction = ({ type }) =>
  /SUCCESS_(.*)/.test(type)
