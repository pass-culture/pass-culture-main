import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferNew from './OfferNew'
import { assignData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'

class OfferNewButton extends Component {
  onClick = () => {
    const { assignData, resetForm, showModal } = this.props
    assignData({ works: null })
    resetForm()
    showModal(<OfferNew />)
  }
  render() {
    return (
      <button className="button is-primary level-item"
        onClick={this.onClick}>
        Nouvelle Offre
      </button>
    )
  }
}

export default connect(
  null,
  { assignData, resetForm, showModal }
)(OfferNewButton)
