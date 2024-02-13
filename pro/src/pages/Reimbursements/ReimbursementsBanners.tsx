import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { BannerReimbursementsInfo } from 'components/Banner'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import PendingBankAccountCallout from 'components/Callout/PendingBankAccountCallout'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './ReimbursementBanners.module.scss'

const ReimbursementsBanners = (): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { selectedOffererId } = useCurrentUser()

  const [isOfferersLoading, setIsOfferersLoading] = useState<boolean>(false)

  const { setSelectedOfferer, selectedOfferer } = useReimbursementContext()

  useEffect(() => {
    const fetchData = async () => {
      setIsOfferersLoading(true)
      try {
        const { offerersNames } = await api.listOfferersNames()

        if (offerersNames.length >= 1) {
          const offerer = await api.getOfferer(
            selectedOffererId || offerersNames[0].id
          )
          setSelectedOfferer(offerer)
        }
        setIsOfferersLoading(false)
      } catch (error) {
        setIsOfferersLoading(false)
      }
    }
    if (isNewBankDetailsJourneyEnabled) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      fetchData()
    }
  }, [])

  if (isOfferersLoading && isNewBankDetailsJourneyEnabled) {
    return <Spinner />
  }

  return (
    <>
      {!isNewBankDetailsJourneyEnabled && <BannerReimbursementsInfo />}
      <div className={styles['banners']}>
        <AddBankAccountCallout titleOnly={true} offerer={selectedOfferer} />
        <PendingBankAccountCallout titleOnly={true} offerer={selectedOfferer} />
        <LinkVenueCallout titleOnly={true} offerer={selectedOfferer} />
      </div>
    </>
  )
}

export default ReimbursementsBanners
