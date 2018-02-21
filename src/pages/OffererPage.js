import React, { Component } from 'react'
import { connect } from 'react-redux'

import OffererEditButton from '../components/OffererEditButton'
import OffersList from '../components/OffersList'
import OfferNewButton from '../components/OfferNewButton'
import SearchInput from '../components/SearchInput'
import { setUserOfferer } from '../reducers/user'

class OffererPage extends Component {
  handleSetUserOfferer = props => {
    const { offererId, setUserOfferer } = props
    setUserOfferer(offererId)
  }
  componentWillMount () {
    this.handleSetUserOfferer(this.props)
  }
  componentWillReceiveProps (nextProps) {
    if (!nextProps.offerer || nextProps.offerer != this.props.offerer) {
      this.handleSetUserOfferer(nextProps)
    }
  }
  render () {
    return (
      <main className='professional-home-page p2'>
        <div className='flex items-center flex-start mt2 mb2'>
          <OfferNewButton />
          <OffererEditButton />
          <SearchInput />
        </div>
        <OffersList />
      </main>
    )
  }
}

export default connect(
  state => ({ offerer: state.user && state.user.offerer }),
  { setUserOfferer }
)(OffererPage)
