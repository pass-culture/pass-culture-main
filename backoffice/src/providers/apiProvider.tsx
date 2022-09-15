import { env } from '../libs/environment/env'
import {
  Configuration,
  ConfigurationParameters,
  DefaultApi,
} from '../TypesFromApi'

export const apiProvider = () => {
  const basePath = env.URL_BASE.replace(/\/+$/, '')
  const accessToken = JSON.parse(localStorage.getItem('tokenApi') as string)
  const confParams = {
    basePath: basePath,
    accessToken: accessToken,
  } as ConfigurationParameters
  const configuration = new Configuration(confParams)

  return new DefaultApi(configuration)
}
