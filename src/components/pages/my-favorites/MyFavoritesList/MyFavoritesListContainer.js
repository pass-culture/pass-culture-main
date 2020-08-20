import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import { selectFavorites } from '../../../../redux/selectors/data/favoritesSelectors'
import { favoriteNormalizer } from '../../../../utils/normalizers'
import { FEATURES } from '../../../router/selectors/features'
import selectIsFeatureDisabled from '../../../router/selectors/selectIsFeatureDisabled'
import MyFavoritesList from './MyFavoritesList'

export const mapStateToProps = state => ({
  isHomepageDisabled: selectIsFeatureDisabled(state, FEATURES.HOMEPAGE),
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
