import React, { Fragment } from 'react'
import { Offerer } from '../Offerer'
import PropTypes from 'prop-types'
import { ROOT_PATH } from '../../../../../utils/config'
import { BankInformationLegacy } from './BankInformationLegacy'

const BankInformation = ({ offerer }) => (
  <div className="section bank-information">
    <h2 className="main-list-title">
      {'Coordonnées bancaires de la structure'}
    </h2>

    {offerer.areBankInformationProvided ? (
      <Fragment>
        <a
          className="bi-external-link bi-external-link--mod-topright"
          href="google.com"
          target="_blank"
        >
          <img
            alt="external-site"
            src={`${ROOT_PATH}/icons/ico-external-site.svg`}
          />
          <b>
            {'Modifier'}
          </b>
        </a>
        <p className="bi-subtitle">
          {
            'Les coordonnées bancaires ci dessous seront attribuées à tous les lieux sans coordonnées bancaires propres :'
          }
        </p>
        <div className="bi-field">
          <span>
            {'IBAN : '}
          </span>
          <span>
            {offerer.iban}
          </span>
        </div>
        <div className="bi-field">
          <span>
            {'BIC : '}
          </span>
          <span>
            {offerer.bic}
          </span>
        </div>
      </Fragment>
    ) : (
      <Fragment>
        <p className="bi-subtitle">
          {'Aucune coordonnée bancaire renseignée'}
        </p>
        <div className="bi-banner">
          <div>
            <p>
              {'Renseigner vos coordonnées bancaires pour être remboursé de vos offres éligibles'}
            </p>

            <p>
              <img
                alt="external-site"
                src={`${ROOT_PATH}/icons/ico-external-site.svg`}
              />
              <a
                className="bi-external-link"
                href="google.com"
                target="_blank"
              >
                {'Renseigner les coordonnées bancaires de la structure'}
              </a>
            </p>
          </div>
        </div>
      </Fragment>
    )}
  </div>
)

BankInformation.propTypes = {
  offerer: PropTypes.instanceOf(Offerer).isRequired,
}

BankInformation.Legacy = BankInformationLegacy
export default BankInformation
