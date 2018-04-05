import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { assignData } from '../reducers/data'
<<<<<<< HEAD
import { resetForm } from '../reducers/form'
=======
>>>>>>> refactor Signup and Signin

const withSign = WrappedComponent => {
  class _withSign extends Component {
    componentWillMount () {
<<<<<<< HEAD
      const { assignData, resetForm } = this.props
      assignData({ errors: null })
      resetForm()
=======
      this.props.assignData({ errors: null })
>>>>>>> refactor Signup and Signin
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
<<<<<<< HEAD
      { assignData, resetForm }
=======
      { assignData }
>>>>>>> refactor Signup and Signin
    )
  )(_withSign)
}

export default withSign
