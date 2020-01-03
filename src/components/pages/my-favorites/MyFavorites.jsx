import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { toast } from 'react-toastify'

import MyFavoriteDetailsContainer from './MyFavoriteDetails/MyFavoriteDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import NoItems from '../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../layout/RelativeFooter/RelativeFooterContainer'
import Teaser from '../../layout/Teaser/TeaserContainer'

const showFailModal = () => {
  toast('La suppression d’un favori a échoué, veuillez ré-essayer plus tard.')
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
    <main className={hasNoFavorite ? 'teaser-main teaser-no-teasers' : 'teaser-main'}>
      {hasNoFavorite ? (
        <NoItems sentence="Dès que vous aurez ajouté une offre en favori," />
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
      <div className="teaser-list">
        <HeaderContainer
          shouldBackFromDetails
          title="Mes favoris"
        />
        {this.renderMyFavorites(
          hasNoFavoriteSelected,
          isEditMode,
          hasNoFavorite,
          myFavorites,
          offerIds
        )}
        <MyFavoriteDetailsContainer bookingPath="/favoris/:details(details|transition)/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/:booking(reservation)?/:bookingId?/:cancellation(annulation)?/:confirmation(confirmation)?" />
        <RelativeFooterContainer
          extraClassName="dotted-top-red"
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
  deleteFavorites: PropTypes.func.isRequired,
  loadMyFavorites: PropTypes.func.isRequired,
  myFavorites: PropTypes.arrayOf(PropTypes.shape()),
}

export default MyFavorites
