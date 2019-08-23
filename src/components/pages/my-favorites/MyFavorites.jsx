import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { toast } from 'react-toastify'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import MyFavoriteContainer from './MyFavorite/MyFavoriteContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NoItems from '../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'

const showFailModal = () => {
  toast('La suppression d’un favoris s’est mal passé, veuillez ré-essayer plus tard.')
}

class MyFavorites extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: true,
      hasError: false,
    }
  }

  componentDidMount = () => {
    const { loadMyFavorites } = this.props
    loadMyFavorites(this.handleFail, this.handleSuccess)
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

  renderMyFavorites = (
    areFavoritesSelected,
    deleteFavorites,
    handleEditMode,
    isEditMode,
    isEmpty,
    myFavorites
  ) => (
    <main className={isEmpty ? 'teaser-main teaser-no-teasers' : 'teaser-main'}>
      {isEmpty ? (
        <NoItems sentence="Dès que vous aurez ajouté une offre en favori," />
      ) : (
        <section>
          {isEditMode ? (
            <div className="mf-edit">
              <button
                className="mf-delete-btn"
                disabled={areFavoritesSelected}
                onClick={deleteFavorites(showFailModal)}
                type="button"
              >
                {'Supprimer la sélection'}
              </button>
              <button
                className="mf-edit-btn"
                onClick={handleEditMode}
                type="button"
              >
                {'Terminer'}
              </button>
            </div>
          ) : (
            <div className="mf-done">
              <button
                className="mf-done-btn"
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

  render() {
    const {
      areFavoritesSelected,
      deleteFavorites,
      handleEditMode,
      isEditMode,
      myFavorites,
    } = this.props
    const { hasError, isLoading } = this.state
    const isEmpty = myFavorites.length === 0

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
        {this.renderMyFavorites(
          areFavoritesSelected,
          deleteFavorites,
          handleEditMode,
          isEditMode,
          isEmpty,
          myFavorites
        )}
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
  areFavoritesSelected: true,
  isEditMode: false,
  myFavorites: [],
}

MyFavorites.propTypes = {
  areFavoritesSelected: PropTypes.bool,
  deleteFavorites: PropTypes.func.isRequired,
  handleEditMode: PropTypes.func.isRequired,
  isEditMode: PropTypes.bool,
  loadMyFavorites: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
  resetPageData: PropTypes.func.isRequired,
}

export default MyFavorites
