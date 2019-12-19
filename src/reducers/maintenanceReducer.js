const FAIL_DATA_PATTERN = 'FAIL_DATA_'
const SUCCESS_DATA_PATTERN = 'SUCCESS_DATA_'
const MAINTENANCE_STATUS_CODE = 500
const SERVER_ERROR = 'SERVER_ERROR'

const initialState = {
  isActivated: false,
}

const maintenanceReducer = (
  state = initialState,
  action = { type: '', payload: { error_type: '' } }
) => {
  const { type: actionType, payload } = action
  const serverErrorDetected =
    actionType.startsWith(FAIL_DATA_PATTERN) &&
    payload.status === MAINTENANCE_STATUS_CODE &&
    payload.error_type === SERVER_ERROR
  if (serverErrorDetected) {
    return Object.assign({}, state, {
      isActivated: true,
    })
  }
  if (actionType.startsWith(SUCCESS_DATA_PATTERN)) {
    return Object.assign({}, state, {
      isActivated: false,
    })
  }
  return state
}

export default maintenanceReducer
