import type { LoaderFunctionArgs } from 'react-router'
import * as reactRouter from 'react-router'

import * as storeModule from '@/commons/store/store'
import { configureTestStore } from '@/commons/store/testUtils'

import { routesSignup } from '../subroutesSignupMap'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    redirect: vi.fn((path: string) => ({ type: 'redirect', path })),
    replace: vi.fn((path: string) => ({ type: 'replace', path })),
  }
})

const createMockLoaderArgs = (url: string): LoaderFunctionArgs =>
  ({
    request: new Request(url),
    params: {},
  }) as LoaderFunctionArgs

const setupStore = (features: string[]) => {
  const store = configureTestStore({
    features: {
      list: features.map((name, i) => ({ id: i, isActive: true, name })),
    },
  })
  vi.spyOn(storeModule, 'rootStore', 'get').mockReturnValue(store)
}

const getInscriptionLoader = () => {
  const route = routesSignup.find((r) => r.path === '/inscription')
  if (!route?.loader) {
    throw new Error('Route /inscription not found or has no loader')
  }
  return route.loader as (args: LoaderFunctionArgs) => unknown
}

describe('routesSignup /inscription loader', () => {
  it('should redirect to /bienvenue when WIP_PRE_SIGNUP_INFO is active', () => {
    setupStore(['WIP_PRE_SIGNUP_INFO'])
    const loader = getInscriptionLoader()
    const args = createMockLoaderArgs('http://localhost/inscription')

    loader(args)

    expect(reactRouter.redirect).toHaveBeenCalledWith('/bienvenue')
    expect(reactRouter.replace).not.toHaveBeenCalled()
  })

  it('should replace to /inscription/compte/creation when WIP_PRE_SIGNUP_INFO is not active', () => {
    setupStore([])
    const loader = getInscriptionLoader()
    const args = createMockLoaderArgs('http://localhost/inscription')

    loader(args)

    expect(reactRouter.replace).toHaveBeenCalledWith(
      '/inscription/compte/creation'
    )
    expect(reactRouter.redirect).not.toHaveBeenCalled()
  })
})
