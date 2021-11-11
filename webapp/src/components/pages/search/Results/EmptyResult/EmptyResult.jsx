import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'

export const EmptyResult = ({ searchedKeywords, onNewSearchAroundMe }) => {
  const noResultMessage =
    searchedKeywords.length > 0
      ? `Pas de résultat trouvé pour "${searchedKeywords}"`
      : 'Pas de résultat trouvé.'

  return (
    <div className="empty-search-result-wrapper">
      <Icon svg="ico-no-offer" />
      <span>
        {'Oups !'}
      </span>
      <p>
        <span>
          {noResultMessage}
        </span>
      </p>
      <p>
        {'Modifie ta recherche ou découvre toutes les offres '}
        <button
          onClick={onNewSearchAroundMe}
          type="button"
        >
          {'autour de chez toi'}
        </button>
      </p>
    </div>
  )
}

EmptyResult.propTypes = {
  onNewSearchAroundMe: PropTypes.func.isRequired,
  searchedKeywords: PropTypes.string.isRequired,
}
