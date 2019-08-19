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

  renderFavoritesList = (editMode, handleEditMode, myFavorites) => {
    const isEmpty = myFavorites.length === 0

    return (
      <main className={isEmpty ? 'teaser-main teaser-no-teasers' : 'teaser-main'}>
        {isEmpty ? (
          <NoItems sentence="Dès que vous aurez ajouté une offre en favori," />
        ) : (
          <section>
            {editMode ? (
              <div className="mf-done">
                <button
                  className="mf-delete-btn"
                  type="button"
                >
                  {'Supprimer la sélection'}
                </button>
                <button
                  className="mf-done-btn"
                  onClick={handleEditMode}
                  type="button"
                >
                  {'Terminer'}
                </button>
              </div>
            ) : (
              <div className="mf-edit">
                <button
                  className="mf-edit-btn"
                  onClick={handleEditMode}
                  type="button"
                >
                  {'Modifier'}
                </button>
              </div>
            )}
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
    )
  }

  render() {
    const { editMode, handleEditMode, myFavorites } = this.props
    const { isLoading, hasError } = this.state

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <div className="teaser-list">
        <HeaderContainer
          shouldBackFromDetails
          title="Mes favoris"
        />
        {this.renderFavoritesList(editMode, handleEditMode, myFavorites)}
        <MyFavoriteDetailsContainer bookingPath="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/:booking(reservation)?/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?" />
        <RelativeFooterContainer
          className="dotted-top-red"
          theme="purple"
        />
      </div>
    )
  }
}

MyFavorites.defaultProps = {
  editMode: false,
  myFavorites: [],
}

MyFavorites.propTypes = {
  editMode: PropTypes.bool,
  handleEditMode: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
  requestGetMyFavorites: PropTypes.func.isRequired,
  resetPageData: PropTypes.func.isRequired,
}

export default MyFavorites
