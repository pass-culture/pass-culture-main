import { requestData } from 'redux-saga-data'

const mapDispatchToProps = (dispatch, ownProps) => {
  const { musicTypes, showTypes } = ownProps
  return {
    handleRequestMusicAndShowTypes: () => {
      if (!musicTypes) {
        dispatch(
          requestData({
            apiPath: '/musicTypes',
          })
        )
      }
      if (!showTypes) {
        dispatch(
          requestData({
            apiPath: '/showTypes',
          })
        )
      }
    },
  }
}

export default mapDispatchToProps
