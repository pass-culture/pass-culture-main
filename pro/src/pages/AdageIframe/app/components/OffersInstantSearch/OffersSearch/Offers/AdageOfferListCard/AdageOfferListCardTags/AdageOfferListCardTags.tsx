import {
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

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
        <Tag
          key={tag.text}
          variant={TagVariant.LIGHT_GREY}
          className={styles['offer-tags-tag']}
        >
          <span aria-hidden="true">{tag.icon}</span> {tag.text}
        </Tag>
      ))}
    </div>
  )
}
