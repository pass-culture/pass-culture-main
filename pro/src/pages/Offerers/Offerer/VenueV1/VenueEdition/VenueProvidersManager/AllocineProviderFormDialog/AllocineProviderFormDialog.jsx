import './AllocineProviderFormDialog.scss'

import PropTypes from 'prop-types'
import React from 'react'

import DialogBox from 'components/DialogBox/DialogBox'

import AllocineProviderForm from '../AllocineProviderForm/AllocineProviderForm'

const AllocineProviderFormDialog = ({
  onCancel,
  onConfirm,
  initialValues,
  providerId,
  venueId,
  offererId,
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
        offererId={offererId}
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
  providerId: PropTypes.number.isRequired,
  venueId: PropTypes.number.isRequired,
  offererId: PropTypes.number.isRequired,
}

export default AllocineProviderFormDialog
