// HOC THAT GATHERS COMMON TASK FOR SIGNIN AND SIGNUP PAGE
// LIKE RESET DATA, FORM REDUCER / REDIRECT TO decouverte ON USER SUCCESS
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'

const withSign = WrappedComponent => {
  class _withSign extends Component {
    componentWillMount () {
      const { assignData, resetForm } = this.props
      assignData({ errors: null })
      resetForm()
    }

    componentWillReceiveProps (nextProps) {
      const { errors, history, user } = nextProps
      if (user && !errors) {
        history.push('/decouverte')
      }
    }

    render () {
      return <WrappedComponent {...this.props} />
    }
  }
  return compose(
    withRouter,
    connect(
      (state, ownProps) => ({
        errors: state.data.errors && state.data.errors.global,
        form: state.form,
        user: state.user
      }),
      { assignData, resetForm }
    )
  )(_withSign)
}

export default withSign
