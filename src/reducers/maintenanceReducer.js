const FAIL_DATA_PATTERN = 'FAIL_DATA_'
const SUCCESS_DATA_PATTERN = 'SUCCESS_DATA_'
const MAINTENANCE_STATUS_CODE = 503

const initialState = {
  isActivated: false,
}

const maintenanceReducer = (state = initialState, action = { type: '' }) => {
  const { type: actionType } = action
  if (
    actionType.startsWith(FAIL_DATA_PATTERN) &&
    action.payload.status === MAINTENANCE_STATUS_CODE
  ) {
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
