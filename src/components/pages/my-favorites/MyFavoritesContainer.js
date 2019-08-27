import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import MyFavorites from './MyFavorites'
import { withRequiredLogin } from '../../hocs'
import { resetPageData } from '../../../reducers/data'
import selectFavorites from '../../../selectors/selectFavorites'
import { favoriteNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => ({
  myFavorites: selectFavorites(state),
})

export const mapDispatchToProps = dispatch => ({
  loadMyFavorites: (handleFail, handleSuccess) => {
    dispatch(
      requestData({
        apiPath: '/favorites',
        handleFail,
        handleSuccess,
        normalizer: favoriteNormalizer,
      })
    )
  },
  deleteFavorites: (showFailModal, offerIds = []) => () => {
    offerIds.forEach(offerId => {
      dispatch(
        requestData({
          apiPath: `/favorites/${offerId}`,
          handleFail: showFailModal,
          method: 'DELETE',
          normalizer: favoriteNormalizer,
        })
      )
    })
  },
  resetPageData: () => {
    dispatch(resetPageData())
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MyFavorites)
