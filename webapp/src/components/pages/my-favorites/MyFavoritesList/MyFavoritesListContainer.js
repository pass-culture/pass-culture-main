import { connect } from 'react-redux'

import { selectFavorites } from '../../../../redux/selectors/data/favoritesSelectors'
import { requestData } from '../../../../utils/fetch-normalize-data/requestData'
import { favoriteNormalizer } from '../../../../utils/normalizers'
import MyFavoritesList from './MyFavoritesList'

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
        })
      )
    })
  },
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MyFavoritesList)
