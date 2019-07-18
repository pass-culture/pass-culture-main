import PropTypes from 'prop-types'
import React, { Component } from 'react'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NavigationFooter from '../../layout/NavigationFooter'
import PageHeader from '../../layout/Header/PageHeader'
import NoFavorites from './NoFavorite/NoFavorites'
import MyFavoriteContainer from './MyFavorite/MyFavoriteContainer'

class MyFavorites extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      isEmpty: false,
      isLoading: true,
    }
  }

  componentDidMount = () => {
    const { getMyFavorites } = this.props

    getMyFavorites(this.handleFail, this.handleSuccess)
  }

  build = myFavorites => (
    <ul>
      {myFavorites.map(myFavorite => (
        <MyFavoriteContainer
          favorite={myFavorite}
          key={myFavorite.id}
        />
      ))}
    </ul>
  )

  handleFail = () => {
    this.setState({
      hasError: true,
      isLoading: true,
    })
  }

  handleSuccess = (state, action) => {
    this.setState({
      isEmpty: action.payload.data.length === 0,
      isLoading: false,
    })
  }

  render() {
    const { myFavorites } = this.props
    const { isEmpty, isLoading, hasError } = this.state

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <div
        className="page is-relative flex-rows"
        id="my-favorites"
      >
        <PageHeader title="Mes préférés" />
        <main className={isEmpty ? 'mf-main mf-no-favorites' : 'mf-main'}>
          {isEmpty && <NoFavorites />}

          {myFavorites.length > 0 && (
            <section className="mf-section">
              <header className="mf-header">{'Favoris'}</header>
              {this.build(myFavorites)}
            </section>
          )}
        </main>
        <NavigationFooter
          className="dotted-top-red"
          theme="purple"
        />
      </div>
    )
  }
}

MyFavorites.propTypes = {
  getMyFavorites: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyFavorites
