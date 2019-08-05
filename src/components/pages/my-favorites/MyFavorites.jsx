import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import MyFavoriteContainer from './MyFavorite/MyFavoriteContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NoItems from '../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'

class MyFavorites extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: true,
      hasError: false,
    }
  }

  componentDidMount = () => {
    const { requestGetMyFavorites } = this.props
    requestGetMyFavorites(this.handleFail, this.handleSuccess)
  }

  componentWillUnmount() {
    const { resetPageData } = this.props
    resetPageData()
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

  renderFavoritesList = () => {
    const { myFavorites } = this.props
    const isEmpty = myFavorites.length === 0

    return (
      <div
        className={classnames('page-content', {
          'teaser-no-teasers': isEmpty,
        })}
      >
        {isEmpty && (
          <NoItems
            sentence="Dès que vous aurez ajouté une offre en favori,"
            withWhiteBackground
          />
        )}

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
      </div>
    )
  }

  render() {
    const { isLoading, hasError } = this.state

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <main
        className="teaser-list page with-header with-footer"
        role="main"
      >
        <HeaderContainer
          shouldBackFromDetails
          title="Mes favoris"
        />
        {this.renderFavoritesList()}
        <MyFavoriteDetailsContainer bookingPath="/favoris/:details(details)/:favoriteId([A-Z0-9]+)/:bookings(reservations)/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?" />
        <RelativeFooterContainer
          className="dotted-top-red"
          theme="purple"
        />
      </main>
    )
  }
}

MyFavorites.defaultProps = {
  myFavorites: [],
}

MyFavorites.propTypes = {
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
  requestGetMyFavorites: PropTypes.func.isRequired,
  resetPageData: PropTypes.func.isRequired,
}

export default MyFavorites
