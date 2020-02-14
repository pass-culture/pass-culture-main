import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

class StockInformationMessage extends PureComponent {
  render(){
    const { providerName } = this.props
    if (providerName === 'Allociné') {
      return (<i>
        {'Il n’est pas possible d’ajouter d’horaires '}
        {'pour cet événement '}
        {providerName}
      </i>)
    }
    return (<i>
      {'Il n’est pas possible d’ajouter ni de supprimer d’horaires '}
      {'pour cet événement '}
      {providerName}
    </i>)
  }
}

StockInformationMessage.propTypes = {
  providerName: PropTypes.string.isRequired,
}

export default StockInformationMessage
