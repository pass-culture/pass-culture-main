import * as contentful from 'contentful'
import { CONTENTFUL_ACCESS_TOKEN, CONTENTFUL_ENVIRONMENT, CONTENTFUL_SPACE_ID } from '../../utils/config'
import { CONTENT_FIELDS, CONTENT_TYPES } from './constants'
import OffersWithCover from '../../components/pages/home/domain/ValueObjects/OffersWithCover'
import Offers from '../../components/pages/home/domain/ValueObjects/Offers'
import BusinessPane from '../../components/pages/home/domain/ValueObjects/BusinessPane'
import ExclusivityPane from '../../components/pages/home/domain/ValueObjects/ExclusivityPane'

const DEPTH_LEVEL = 2

const matchesContentType = (module, contentType) => {
  const { sys: { contentType: { sys: { id } } } } = module
  return id === contentType
}

const initClient = () => {
  return contentful.createClient({
    accessToken: CONTENTFUL_ACCESS_TOKEN,
    environment: CONTENTFUL_ENVIRONMENT,
    space: CONTENTFUL_SPACE_ID
  })
}

export const fetchLastHomepage = () => {
  const client = initClient()
  return client.getEntries({ content_type: CONTENT_TYPES.HOMEPAGE, include: DEPTH_LEVEL })
    .then(data => {
      const { items } = data
      const lastPublishedHomepage = items[0]
      const { fields: { modules } } = lastPublishedHomepage

      return modules.map(module => {
        const { fields } = module

        if (matchesContentType(module, CONTENT_TYPES.ALGOLIA)) {
          const algoliaParameters = fields[CONTENT_FIELDS.ALGOLIA].fields
          const displayParameters = fields[CONTENT_FIELDS.DISPLAY].fields

          return CONTENT_FIELDS.COVER in fields ?
            new OffersWithCover({
              algolia: algoliaParameters,
              cover: `https:${fields[CONTENT_FIELDS.COVER].fields[CONTENT_FIELDS.IMAGE].fields[CONTENT_FIELDS.FILE].url}`,
              display: displayParameters
            }) :
            new Offers({
              algolia: algoliaParameters,
              display: displayParameters
            })
        } else {
          if (matchesContentType(module, CONTENT_TYPES.EXCLUSIVITY)) {
            return new ExclusivityPane({
              alt: fields[CONTENT_FIELDS.ALT],
              image: `https:${fields[CONTENT_FIELDS.IMAGE].fields[CONTENT_FIELDS.FILE].url}`,
              offerId: fields[CONTENT_FIELDS.OFFER_ID]
            })
          }
          return new BusinessPane({
            firstLine: fields[CONTENT_FIELDS.FIRST_LINE],
            image: `https:${fields[CONTENT_FIELDS.IMAGE].fields[CONTENT_FIELDS.FILE].url}`,
            secondLine: fields[CONTENT_FIELDS.SECOND_LINE],
            url: fields[CONTENT_FIELDS.URL]
          })
        }
      })
    })
    .catch(() => {
      return []
    })
}
