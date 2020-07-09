import * as contentful from 'contentful'
import { CONTENTFUL_ACCESS_TOKEN, CONTENTFUL_ENVIRONMENT, CONTENTFUL_SPACE_ID } from '../../utils/config'
import { CONTENT_FIELDS, CONTENT_TYPES } from './constants'
import OffersWithCover from '../../components/pages/home/domain/ValueObjects/OffersWithCover'
import Offers from '../../components/pages/home/domain/ValueObjects/Offers'
import InformationPane from '../../components/pages/home/domain/ValueObjects/InformationPane'

const DEPTH_LEVEL = 2

const isAlgoliaModule = module => {
  const { sys: { contentType: { sys: { id } } } } = module
  return id === CONTENT_TYPES.ALGOLIA
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

        if (isAlgoliaModule(module)) {
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
          return new InformationPane({
            image: `https:${fields[CONTENT_FIELDS.IMAGE].fields[CONTENT_FIELDS.FILE].url}`,
            title: fields[CONTENT_FIELDS.TITLE],
            url: fields[CONTENT_FIELDS.URL]
          })
        }
      })
    })
}
