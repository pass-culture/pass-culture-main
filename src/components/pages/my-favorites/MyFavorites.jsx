import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Route, Switch } from 'react-router'
import { toast } from 'react-toastify'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NoItems from '../../layout/NoItems/NoItems'
import Teaser from '../../layout/Teaser/TeaserContainer'

const showFailModal = () => {
  toast.error('La suppression d’un favori a échoué, réessaie plus tard.')
}

class MyFavorites extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      isEditMode: false,
      isLoading: true,
      hasError: false,
      offerIds: [],
    }
  }

  componentDidMount = () => {
    const { loadMyFavorites } = this.props
    loadMyFavorites(this.handleFail, this.handleSuccess)
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

  handleEditMode = () => {
    this.setState(previousState => ({
      isEditMode: !previousState.isEditMode,
      offerIds: [],
    }))
  }

  onToggle = offerId => () => {
    let { offerIds } = this.state
    let isUpdated = true

    offerIds = offerIds.reduce((favoritesToDelete, currentFavorite) => {
      if (currentFavorite === offerId) {
        isUpdated = false
      } else {
        favoritesToDelete.push(currentFavorite)
      }

      return favoritesToDelete
    }, [])

    if (isUpdated) {
      offerIds.push(offerId)
    }

    // Ceci n'est pas la bonne façon de faire d'après :
    // https://reactjs.org/docs/react-component.html#setstate
    // Il faudrait plutôt utiliser une fonction mais comme elle tourne deux fois
    // d'affilé, je n'ai pas eu le choix.
    this.setState({
      offerIds,
    })
  }

  deleteFavorites = (showFailModal, offerIds) => () => {
    const { deleteFavorites } = this.props

    this.setState({ offerIds: [] }, deleteFavorites(showFailModal, offerIds))
  }

  renderMyFavorites = (hasNoFavoriteSelected, isEditMode, hasNoFavorite, myFavorites, offerIds) => (
    <main className="teaser-page">
      <h1 className="teaser-main-title">
        {'Favoris'}
      </h1>
      {hasNoFavorite ? (
        <NoItems sentence="Dès que tu auras ajouté une offre en favori, tu la retrouveras ici." />
      ) : (
        <section>
          {isEditMode ? (
            <div className="mf-edit">
              <button
                className="mf-delete-btn"
                disabled={hasNoFavoriteSelected}
                onClick={this.deleteFavorites(showFailModal, offerIds)}
                type="button"
              >
                {'Supprimer la sélection'}
              </button>
              <button
                className="mf-done-btn"
                onClick={this.handleEditMode}
                type="button"
              >
                {'Terminer'}
              </button>
            </div>
          ) : (
            <div className="mf-done">
              <button
                className="mf-edit-btn"
                onClick={this.handleEditMode}
                type="button"
              >
                {'Modifier'}
              </button>
            </div>
          )}
          <ul>
            {myFavorites.map(myFavorite => (
              <Teaser
                handleToggleTeaser={this.onToggle}
                isEditMode={isEditMode}
                item={myFavorite}
                key={myFavorite.id}
              />
            ))}
          </ul>
        </section>
      )}
    </main>
  )

  render() {
    const { myFavorites } = this.props
    const { isEditMode, isLoading, hasError, offerIds } = this.state
    const hasNoFavorite = myFavorites.length === 0
    const hasNoFavoriteSelected = offerIds.length === 0

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <Switch>
        <Route
          exact
          path="/favoris"
        >
          {this.renderMyFavorites(
            hasNoFavoriteSelected,
            isEditMode,
            hasNoFavorite,
            myFavorites,
            offerIds
          )}
        </Route>
        <Route
          exact
          path="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
          sensitive
        >
          <HeaderContainer
            shouldBackFromDetails
            title="Favoris"
          />
          <MyFavoriteDetailsContainer bookingPath="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId(vide|[A-Z0-9]+)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?" />
        </Route>
      </Switch>
    )
  }
}

MyFavorites.defaultProps = {
  myFavorites: [],
}

MyFavorites.propTypes = {
  deleteFavorites: PropTypes.func.isRequired,
  loadMyFavorites: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
}

export default MyFavorites
