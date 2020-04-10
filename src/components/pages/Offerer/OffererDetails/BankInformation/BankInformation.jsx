import React from 'react'
import BankInformationLegacy from './BankInformationLegacy'
import { Offerer } from '../Offerer'
import PropTypes from 'prop-types'
import { ROOT_PATH } from '../../../../../utils/config'

const BankInformation = ({ offerer }) => (
  <div className="section">
    <h2 className="main-list-title">
      {'Coordonnées bancaires de la structure'}
    </h2>

    {offerer.areBankInformationProvided ? (
      <div>
        <div>
          <span>
            {'BIC : '}
          </span>
          <span>
            {offerer.bic}
          </span>
        </div>
        <div>
          <span>
            {'IBAN : '}
          </span>
          <span>
            {offerer.iban}
          </span>
        </div>
      </div>
    ) : (
      <div>
        <p>
          {'Aucune coordonnée bancaire renseignée'}
        </p>
        <div>
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
                href="google.com"
                target="_blank"
              >
                {'Renseigner les coordonnées bancaires de la structure'}
              </a>
            </p>
          </div>
        </div>
      </div>
    )}
  </div>
)

BankInformation.propTypes = {
  offerer: PropTypes.instanceOf(Offerer).isRequired,
}

BankInformation.Legacy = BankInformationLegacy
export default BankInformation
