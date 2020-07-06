import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import MyFavoritesList from './MyFavoritesList'
import { selectFavorites } from '../../../../redux/selectors/data/favoritesSelectors'
import { favoriteNormalizer } from '../../../../utils/normalizers'

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
  persistDeleteFavorites: (showFailModal, offerIds = []) => {
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

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MyFavoritesList)
