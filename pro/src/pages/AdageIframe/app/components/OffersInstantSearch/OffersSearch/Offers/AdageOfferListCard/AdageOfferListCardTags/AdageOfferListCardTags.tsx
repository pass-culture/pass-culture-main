import {
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { Tag } from 'design-system/Tag/Tag'

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
  const tags = getOfferTags(offer, adageUser)

  return (
    <div className={styles['offer-tags']}>
      {tags.map((tag) => (
        <Tag key={tag.text} label={tag.text} />
      ))}
    </div>
  )
}
