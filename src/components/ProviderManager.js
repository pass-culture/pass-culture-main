import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
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
            collectionName="offerer_providers"
            label={<Label title="La source" />}
            name="bookingEmail"
            options={providers}
            type="select"
          />
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
