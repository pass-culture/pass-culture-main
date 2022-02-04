import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'

import { mapBrowserToApi } from '../../utils/translate'

export const CREATION = 'creation'
export const MODIFICATION = 'modification'

const withFrenchQueryRouter = withQueryRouter({
  mapper: mapBrowserToApi,
})

export default withFrenchQueryRouter
