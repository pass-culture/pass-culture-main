import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useNotification from 'hooks/useNotification'

import AllocineProviderFormDialog from '../AllocineProviderFormDialog/AllocineProviderFormDialog'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'
import VenueProviderItem from '../VenueProviderItem/VenueProviderItem'

const AllocineProviderItem = ({
  afterVenueProviderEdit,
  venueProvider,
  venueDepartmentCode,
}) => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notify = useNotification()

  const editVenueProvider = useCallback(
    payload => {
      api
        .updateVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit({ editedVenueProvider })
          notify.success(
            'Les modifications ont bien été importées et s’appliqueront aux nouvelles séances créées.'
          )
        })
        .catch(error => {
          if (isErrorAPIError(error)) {
            notify.error(getRequestErrorStringFromErrors(getError(error)))
          }
        })
    },
    [afterVenueProviderEdit]
  )

  const openFormDialog = useCallback(() => {
    setIsOpenedFormDialog(true)
  }, [])

  const closeFormDialog = useCallback(() => {
    setIsOpenedFormDialog(false)
  }, [])

  const onConfirmDialog = useCallback(
    payload => {
      editVenueProvider(payload)

      closeFormDialog()
    },
    [closeFormDialog, editVenueProvider]
  )

  const initialValues = {
    price: venueProvider.price,
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo,
    isActive: venueProvider.isActive,
  }

  return (
    <VenueProviderItem
      venueDepartmentCode={venueDepartmentCode}
      venueProvider={venueProvider}
    >
      <>
        <li>
          <span>{'Prix de vente/place : '}</span>
          <span>
            {`${new Intl.NumberFormat('fr-FR', {
              style: 'currency',
              currency: 'EUR',
            }).format(venueProvider.price)}`}
          </span>
        </li>
        <li>
          <span>{'Nombre de places/séance : '}</span>
          <span>
            {`${venueProvider.quantity ? venueProvider.quantity : 'Illimité'}`}
          </span>
        </li>
        <li>
          <span>{'Accepter les offres DUO : '}</span>
          <span>{`${venueProvider.isDuo ? 'Oui' : 'Non'} `}</span>
        </li>
        <button
          className="primary-button"
          onClick={openFormDialog}
          type="button"
        >
          Modifier les paramètres
        </button>
        {isOpenedFormDialog && (
          <AllocineProviderFormDialog
            initialValues={initialValues}
            onCancel={closeFormDialog}
            onConfirm={onConfirmDialog}
            providerId={venueProvider.providerId}
            venueId={venueProvider.venueId}
          />
        )}
      </>
    </VenueProviderItem>
  )
}

AllocineProviderItem.propTypes = {
  afterVenueProviderEdit: PropTypes.func.isRequired,
  venueDepartmentCode: PropTypes.string.isRequired,
  venueProvider: PropTypes.shape({
    provider: PropTypes.shape({
      name: PropTypes.string.isRequired,
    }).isRequired,
    providerId: PropTypes.string.isRequired,
    venueId: PropTypes.string.isRequired,
    lastSyncDate: PropTypes.string,
    nOffers: PropTypes.number.isRequired,
    venueIdAtOfferProvider: PropTypes.string,
    price: PropTypes.number,
    quantity: PropTypes.number,
    isDuo: PropTypes.bool,
  }).isRequired,
}

export default AllocineProviderItem
