import { useLocation } from 'react-router-dom'

import { parse } from 'utils/query-string'

export const useUtmQueryParams = () => {
  const location = useLocation()
  const parsedParams = parse(location.search)
  const hasUtmQueryParams =
    'utm_campaign' in parsedParams &&
    'utm_medium' in parsedParams &&
    'utm_source' in parsedParams
  return hasUtmQueryParams
    ? {
        traffic_campaign: parsedParams.utm_campaign,
        traffic_medium: parsedParams.utm_medium,
        traffic_source: parsedParams.utm_source,
      }
    : {}
}
