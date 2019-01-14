import { withLogin, withPagination } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RawOfferers from './RawIndex'
import offerersSelector, {
  getPendingOfferers,
} from '../../../selectors/offerers'
import { mapApiToWindow, windowToApiQuery } from '../../../utils/pagination'

function mapStateToProps(state, ownProps) {
  return {
    pendingOfferers: getPendingOfferers(state),
    offerers: offerersSelector(state),
    user: state.user,
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withPagination({
    dataKey: 'offerers',
    defaultWindowQuery: {
      [mapApiToWindow.keywords]: null,
    },
    windowToApiQuery,
  }),
  connect(mapStateToProps)
)(RawOfferers)
