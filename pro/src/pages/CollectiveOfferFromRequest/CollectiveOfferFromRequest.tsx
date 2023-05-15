import React, { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { createOfferFromTemplate } from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'

const CollectiveOfferFromRequest = (): JSX.Element => {
  const navigate = useNavigate()
  const notify = useNotification()

  const { offerId } = useParams<{
    offerId: string
  }>()

  useEffect(() => {
    if (offerId) {
      createOfferFromTemplate(navigate, notify, parseInt(offerId), true)
    } else {
      navigate('/accueil')
    }
  }, [offerId, navigate, notify])

  return <Spinner />
}

export default CollectiveOfferFromRequest
