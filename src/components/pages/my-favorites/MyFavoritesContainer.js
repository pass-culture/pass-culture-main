import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import MyFavorites from './MyFavorites'
import { withRequiredLogin } from '../../hocs'
import { resetPageData } from '../../../reducers/data'
import { toggleFavoritesEditMode } from '../../../reducers/favorites'
import selectAreNotFavoritesSelected from '../../../selectors/selectAreNotFavoritesSelected'
import selectIsFavoritesEditMode from '../../../selectors/selectIsFavoritesEditMode'
import selectDeletedofferIds from '../../../selectors/selectDeletedFavorites'
import selectFavorites from '../../../selectors/selectFavorites'
import { favoriteNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => ({
  areFavoritesSelected: selectAreNotFavoritesSelected(state),
  isEditMode: selectIsFavoritesEditMode(state),
  myFavorites: selectFavorites(state),
  offerIds: selectDeletedofferIds(state),
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

    dispatch(toggleFavoritesEditMode())
  },
  handleEditMode: () => {
    dispatch(toggleFavoritesEditMode())
  },
  resetPageData: () => {
    dispatch(resetPageData())
  },
})

export const mergeProps = (stateProps, dispatchProps) => {
  const { offerIds } = stateProps
  const { deleteFavorites } = dispatchProps

  return {
    ...stateProps,
    ...dispatchProps,
    deleteFavorites: showFailModal => deleteFavorites(showFailModal, offerIds),
  }
}

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(MyFavorites)
