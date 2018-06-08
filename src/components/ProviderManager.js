import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import ProviderItem from './ProviderItem'
import { requestData } from '../reducers/data'
import selectProviderOptions from '../selectors/providerOptions'
import selectCurrentVenue from '../selectors/currentVenue'

class ProviderManager extends Component {

  constructor () {
    super()
    this.state = {
      isNew: false
    }
  }

  onAddClick = () => {
    this.setState({ isNew: true })
  }

  onConfirmClick = e => {
    const { onProviderConfirmClick } = this.props
    this.setState({})
    onProviderConfirmClick && onProviderConfirmClick(e)
  }

  componentDidMount () {
    this.props.requestData('GET', 'providers')
  }

  render () {
    const {
      venueProviders,
      providers
    } = this.props
    const {
      isNew
    } = this.state
    console.log('providers', providers, venueProviders)
    return [
      <h2 className='subtitle is-2' key={0}>
        Mes fournisseurs
      </h2>,
      <button className="button is-primary level-item"
        onClick={this.onAddClick} key={1}>
        Ajouter un fournisseur
      </button>,
      isNew && (
        <div className='box' key={2}>
          <FormField
            collectionName="venue_providers"
            label={<Label title="La source" />}
            name="providerId"
            options={providers}
            type="select"
          />
          <FormField
            collectionName="venue_providers"
            label={<Label title="Mon identifiant" />}
            name="identifiant"
          />
          <button
            className="button"
            onClick={this.onConfirmClick}>
            Ajouter
          </button>
        </div>
      ),
      venueProviders && venueProviders.map((op, index) => (
        <ProviderItem {...op} key={index} />
      ))
    ]
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => Object.assign(
      {
        providers: selectProviderOptions(state)
      },
      selectCurrentVenue(state, ownProps)
    ),
    { requestData }
  )
)(ProviderManager)
