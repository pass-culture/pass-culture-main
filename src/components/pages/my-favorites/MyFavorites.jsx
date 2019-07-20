import PropTypes from 'prop-types'
import React, { Component } from 'react'

import LoaderContainer from '../../layout/Loader/LoaderContainer'
import MyFavoriteContainer from './MyFavorite/MyFavoriteContainer'
import NavigationFooter from '../../layout/NavigationFooter'
import NoItems from '../../layout/NoItems/NoItems'
import PageHeader from '../../layout/Header/PageHeader'

class MyFavorites extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      isLoading: true,
    }
  }

  componentDidMount = () => {
    const { getMyFavorites } = this.props
    getMyFavorites(this.handleFail, this.handleSuccess)
  }

  handleFail = () => {
    this.setState({
      hasError: true,
      isLoading: true,
    })
  }

  handleSuccess = () => {
    this.setState({
      isLoading: false,
    })
  }

  render() {
    const { myFavorites } = this.props
    const { isLoading, hasError } = this.state
    const isEmpty = myFavorites.length === 0

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <div className="teaser-list">
        <PageHeader title="Mes favoris" />
        <main className={isEmpty ? 'teaser-main teaser-no-teasers' : 'teaser-main'}>
          {isEmpty && <NoItems sentence="Dès que vous aurez ajouté une offre en favori," />}

          {!isEmpty && (
            <section>
              <ul>
                {myFavorites.map(myFavorite => (
                  <MyFavoriteContainer
                    favorite={myFavorite}
                    key={myFavorite.id}
                  />
                ))}
              </ul>
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

MyFavorites.defaultProps = {
  myFavorites: [],
}

MyFavorites.propTypes = {
  getMyFavorites: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
}

export default MyFavorites
