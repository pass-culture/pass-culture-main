import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import ProviderItem from './ProviderItem'
import { requestData } from '../reducers/data'
import selectProviderOptions from '../selectors/providerOptions'

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
      offererProviders,
      providers
    } = this.props
    const {
      isNew
    } = this.state
    console.log('providers', providers)
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
      offererProviders && offererProviders.map((op, index) => (
        <ProviderItem {...op} key={index} />
      ))
    ]
  }
}

export default connect(
  state => ({ providers: selectProviderOptions(state) }),
  { requestData }
)(ProviderManager)
