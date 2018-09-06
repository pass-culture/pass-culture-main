/* eslint-disable */
import PropTypes from 'prop-types'
import moment from 'moment'
import React from 'react'

export const SearchFilter = ({
  handleClearQueryParams,
  handleQueryParamsChange,
}) => (
  <div className="search-filter">
    <form />
    <div>
      <h2>DATE</h2>
      <div className="field checkbox">
        <label id="from_date" className="label">
          Tout de suite !
        </label>
        <input
          id="from_date"
          className="input is-normal"
          onChange={() => handleQueryParamsChange({ from_date: moment.now() })}
          type="checkbox"
        />
      </div>
      <div className="field checkbox">
        <label id="from_date" className="label">
          Entre 1 et 5 jours
        </label>
        <input
          id="from_date"
          className="input is-normal"
          onChange={() => handleQueryParamsChange({ from_date: moment.now() })}
          type="checkbox"
        />
      </div>
    </div>
    <div>
      <h2>DISTANCE</h2>
      <select
        name="select"
        className="select"
        onChange={() => handleQueryParamsChange({ distance: 'value' })}>
        {/*  { distance: 1 } */}
        <option value="1">Moins d'1 km</option>
        <option value="2">Moins de 10 km</option>
        <option value="3">Moins de 50 km</option>
        <option value="4">Toutes distances</option>
      </select>
    </div>
    <div>
      <h2>QUOI</h2>
      <div className="field checkbox">
        <label id="from_date" className="label">
          Applaudir
        </label>
        <input
          id="from_date"
          className="input is-normal"
          onChange={() => handleQueryParamsChange({ from_date: moment.now() })}
          type="checkbox"
        />
      </div>
    </div>

    <button className="button" type="button" onClick={handleClearQueryParams}>
      Réinitialiser
    </button>
    <button className="button" type="submit">
      Filtrer
    </button>
  </div>
)

SearchFilter.propTypes = {
  handleClearQueryParams: PropTypes.func.isRequired,
  handleQueryParamsChange: PropTypes.func.isRequired,
}
