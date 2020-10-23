import { closeModal } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Block from './Block'

export function mapDispatchToProps(dispatch, ownProps) {
  return {
    onConfirmation: () => {
      const {
        unblock,
        nextLocation: { pathname, search },
        history,
      } = ownProps
      dispatch(closeModal())
      unblock()
      history.push(`${pathname}${search}`)
    },
    onCancel: () => {
      dispatch(closeModal())
    },
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(Block)
