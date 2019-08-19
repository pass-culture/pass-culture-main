import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import MyFavorites from './MyFavorites'
import { withRequiredLogin } from '../../hocs'
import { resetPageData } from '../../../reducers/data'
import { toggleFavoritesEditMode } from '../../../reducers/favorites'
import selectFavorites from '../../../selectors/selectFavorites'
import selectIsFavoritesEditMode from '../../../selectors/selectIsFavoritesEditMode'
import { favoriteNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => ({
  editMode: selectIsFavoritesEditMode(state),
  myFavorites: selectFavorites(state),
})

export const mapDispatchToProps = dispatch => ({
  requestGetMyFavorites: (handleFail, handleSuccess) => {
    dispatch(
      requestData({
        apiPath: '/favorites',
        handleFail,
        handleSuccess,
        normalizer: favoriteNormalizer,
      })
    )
  },
  handleEditMode: () => {
    dispatch(toggleFavoritesEditMode())
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
