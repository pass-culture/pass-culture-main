import {
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient//adage'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Tag } from '@/design-system/Tag/Tag'

import { getOfferTags } from '../../utils/getOfferTags'
import styles from './AdageOfferListCardTags.module.scss'

type AdageOfferListCardTagsProps = {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  adageUser: AuthenticatedResponse
}

export function AdageOfferListCardTags({
  offer,
  adageUser,
}: AdageOfferListCardTagsProps) {
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const tags = getOfferTags(offer, adageUser, true, isCollectiveOaActive)

  return (
    <div className={styles['offer-tags']}>
      {tags.map((tag) => (
        <Tag key={tag.text} label={tag.text} icon={tag.icon} />
      ))}
    </div>
  )
}
