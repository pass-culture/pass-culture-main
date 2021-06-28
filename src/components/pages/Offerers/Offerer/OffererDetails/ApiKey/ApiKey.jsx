import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { ApiKeyType } from 'components/pages/Offerers/Offerer/OffererDetails/Offerer'
import { ENV_WORDING } from 'utils/config'

const ApiKey = ({ apiKey }) => {
  return (
    <div className="section op-content-section api-key">
      <div className="main-list-title">
        <h2 className="main-list-title-text">
          {"Gestion des clefs d'API"}
        </h2>
      </div>
      <Banner
        href="https://www.notion.so/passcultureapp/pass-Culture-Int-grations-techniques-231e16685c9a438b97bdcd7737cdd4d1"
        linkTitle="En savoir plus sur les clés d'API"
        type="notification-info"
      />
      <div className="api-key-title">
        <div className="api-key-title__text">
          {'API '}
          {ENV_WORDING}
        </div>
        <div
          className={`api-key-title__counter${
            apiKey.prefixes.length >= apiKey.maxAllowed ? ' api-key-title__counter--error' : ''
          }`}
        >
          {apiKey.prefixes.length}
          {'/'}
          {apiKey.maxAllowed}
        </div>
      </div>
      <div className="api-key-info">
        {"Vous pouvez avoir jusqu'à "}
        {apiKey.maxAllowed}
        {" clefs d'API."}
      </div>
      <div className="api-keys">
        {apiKey.prefixes.map(prefix => {
          return (
            <div
              className="api-keys__item"
              key={prefix}
            >
              {prefix}
              {'********'}
            </div>
          )
        })}
      </div>
    </div>
  )
}
ApiKey.propTypes = {
  apiKey: PropTypes.instanceOf(ApiKeyType).isRequired,
}

export default ApiKey
