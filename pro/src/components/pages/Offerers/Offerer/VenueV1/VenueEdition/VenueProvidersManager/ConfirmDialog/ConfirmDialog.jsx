/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import Icon from 'components/layout/Icon'

import { ReactComponent as AlertSvg } from './assets/ico-alert-grey.svg'
import './ConfirmDialog.scss'

const ConfirmDialog = ({ onConfirm, onCancel }) => {
  return (
    <DialogBox
      extraClassNames="provider-import-confirmation-dialog"
      labelledBy="provider-import-confirmation-dialog"
      onDismiss={onCancel}
    >
      <AlertSvg />
      <div className="title">
        <strong>
          Certains ouvrages seront exclus de la synchronisation automatique.
        </strong>
      </div>
      <div className="explanation">
        <p>
          Vous pouvez retrouver la liste des catégories de livres qui sont exclus de la
          synchronisation automatique en suivant le lien
          <a
            className="tertiary-link"
            href="https://aide.passculture.app/fr/articles/5394935-acteurs-culturels-pourquoi-la-remontee-de-mes-stocks-n-integre-pas-toutes-les-references"
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon
              alt=""
              svg="ico-external-site-red"
            />
            FAQ
          </a>
        </p>
      </div>
      <div className="actions">
        <button
          className="secondary-button"
          onClick={onCancel}
          type="button"
        >
          Annuler
        </button>
        <button
          className="primary-button confirm"
          onClick={onConfirm}
          type="button"
        >
          Continuer
        </button>
      </div>
    </DialogBox>
  )
}

ConfirmDialog.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
}

export default ConfirmDialog
