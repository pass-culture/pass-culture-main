import { parseEnvVariables } from '../parser'

describe('parseEnvVariables', () => {
  const mockedConfig = {
    TEST_BOOLEAN: 'true',
    NODE_ENV: 'development',
    ENV: 'testing',
    OIDC_CLIENT_ID: 'XYZ',
    AUTH_ISSUER: 'https://accounts.google.com/',
    OIDC_REDIRECT_URI: 'http://pc-backoffice-testing.web.app/',
    BASE_PATH: '/backoffice',
    URL_BASE: 'https://backend.testing.passculture.team',
    SAMPLE_RATE: '0.1',
    SENTRY_DSN: 'https://sentrydsn',
  }
  const convertedConfig = parseEnvVariables(mockedConfig)

  it('convert "0.1" in string to float', () => {
    expect(convertedConfig.SAMPLE_RATE).toBe(0.1)
  })

  it('convert "true" in string to true in boolean', () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore TODO: replace with useful boolean when available
    expect(convertedConfig.TEST_BOOLEAN).toBe(true)
  })
  it('convert "false" in string to false in boolean', () => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore TODO: replace with useful boolean when available
    const { TEST_BOOLEAN } = parseEnvVariables({
      ...mockedConfig,
      TEST_BOOLEAN: 'false',
    })
    expect(TEST_BOOLEAN).toBe(false)
  })

  it(`doesn't alter non boolean value`, () => {
    expect(convertedConfig.SENTRY_DSN).toEqual('https://sentrydsn')
  })
})
