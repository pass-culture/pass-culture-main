import React, { useState, useEffect } from 'react'
import { useHistory } from 'react-router'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { getOfferAdapter } from 'core/OfferEducational'
import { OfferEducationalStockFormValues } from 'core/OfferEducationalStock/types'
import { Offer } from 'custom_types/offer'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postEducationalStockAdapter from './adapters/postEducationalStock'

const OfferEducationalStockCreation = (): JSX.Element => {
  const [offer, setOffer] = useState<Offer | null>(null)
  const [isReady, setIsReady] = useState<boolean>(false)
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()

  const initialValues: OfferEducationalStockFormValues = {
    eventDate: '',
    eventTime: '',
    numberOfPlaces: '',
    totalPrice: '',
    bookingLimitDatetime: '',
  }

  const handleSubmitStock = async (
    offer: Offer,
    values: OfferEducationalStockFormValues
  ) => {
    const { isOk, message } = await postEducationalStockAdapter({
      offer,
      values,
    })

    if (!isOk) {
      return notify.error(message)
    }
    history.push('/offre/scolaire/confirmation')
  }

  useEffect(() => {
    if (!isReady) {
      const loadOffer = async () => {
        const { payload, message, isOk } = await getOfferAdapter(offerId)
        if (isOk) {
          setOffer(payload.offer)
          setIsReady(true)
          return
        }
        notify.error(message)
      }

      loadOffer()
    }
  }, [offerId, notify, isReady])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.STOCKS}
      isCreatingOffer
      title="Créer une nouvelle offre scolaire"
    >
      {offer && isReady ? (
        <OfferEducationalStockScreen
          initialValues={initialValues}
          offer={offer}
          onSubmit={handleSubmitStock}
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalStockCreation
