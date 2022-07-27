import './AllocineProviderFormDialog.scss'

import PropTypes from 'prop-types'
import React from 'react'

import DialogBox from 'new_components/DialogBox/DialogBox'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'

const AllocineProviderFormDialog = ({
  onCancel,
  onConfirm,
  initialValues,
  providerId,
  venueId,
}) => {
  return (
    <DialogBox
      extraClassNames="allocine-provider-form-dialog"
      labelledBy="allocine-provider-form-dialog"
      onDismiss={onCancel}
    >
      <div className="title">
        <strong>Modifier les paramètres de mes offres</strong>
      </div>
      <div className="explanation">
        Les modifications s’appliqueront uniquement aux nouvelles offres créées.
        La modification doit être faite manuellement pour les offres existantes.
      </div>
      <AllocineProviderForm
        initialValues={initialValues}
        onCancel={onCancel}
        providerId={providerId}
        saveVenueProvider={onConfirm}
        venueId={venueId}
      />
    </DialogBox>
  )
}

AllocineProviderFormDialog.propTypes = {
  initialValues: PropTypes.shape({
    price: PropTypes.number.isRequired,
    quantity: PropTypes.number.isRequired,
    isDuo: PropTypes.bool.isRequired,
  }).isRequired,
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  providerId: PropTypes.string.isRequired,
  venueId: PropTypes.string.isRequired,
}

export default AllocineProviderFormDialog
