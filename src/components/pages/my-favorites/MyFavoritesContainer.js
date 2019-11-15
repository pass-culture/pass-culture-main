import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import MyFavorites from './MyFavorites'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import { selectFavorites } from '../../../selectors/data/favoritesSelectors'
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
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MyFavorites)
