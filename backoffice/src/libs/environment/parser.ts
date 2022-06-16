import { Environment } from './types'

export const parseEnvVariables = (
  config: Record<string, string | boolean | number>
): Environment => {
  const parsedConfig = { ...config } as Record<
    keyof Environment,
    string | boolean | number
  >

  Object.keys(config).forEach(key => {
    if (config[key] === 'true') {
      parsedConfig[key as keyof Environment] = true
    } else if (config[key] === 'false') {
      parsedConfig[key as keyof Environment] = false
    }
  })

  Object.keys(parsedConfig).forEach(key => {
    if (!isNaN(config[key] as number) && config[key].toString().includes('.')) {
      parsedConfig[key as keyof Environment] = parseFloat(
        (parsedConfig as Record<string, unknown>)[key] as string
      )
    } else {
      parsedConfig[key as keyof Environment] = (
        parsedConfig as Record<string, string | boolean | number>
      )[key]
    }
  })

  return parsedConfig as Environment
}
