import { Component } from 'react'

import { withQueryRouter } from '../withQueryRouter'

export class Test extends Component {
  componentDidUpdate(prevProps) {
    const { onUpdate } = this.props
    if (onUpdate) {
      onUpdate(this.props, prevProps)
    }
  }
  render() {
    return null
  }
}

export const QueryRouterTest = withQueryRouter()(Test)

export const FrenchQueryRouterTest = withQueryRouter({
  creationKey: 'nouveau',
  mapper: {
    lieu: 'venue',
  },
  modificationKey: 'changement',
})(Test)
