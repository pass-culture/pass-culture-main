// HOC THAT GATHERS COMMON TASK FOR SIGNIN AND SIGNUP PAGE
// LIKE RESET DATA, FORM REDUCER / REDIRECT TO decouverte ON USER SUCCESS
import { resetErrors } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { resetForm } from '../../reducers/form'

const withSign = WrappedComponent => {
  class _withSign extends Component {
    constructor (props) {
      super()
    }

    componentDidUpdate() {
      const { errors, history, user } = this.props
      if (user && !errors) {
        // TODO: kind of dirty, find a better check
        if (window.location.pathname === '/inscription') {
          history.push('/structures')
        } else {
          history.push('/offres')
        }
      }
    }

    componentWillUnmount() {
      this.props.resetErrors()
      this.props.resetForm()
    }

    render() {
      return <WrappedComponent {...this.props} />
    }
  }
  return compose(
    withRouter,
    connect(
      (state, ownProps) => ({
        errors: state.errors.global,
        form: state.form,
        user: state.user,
      }),
      { resetErrors, resetForm }
    )
  )(_withSign)
}

export default withSign
