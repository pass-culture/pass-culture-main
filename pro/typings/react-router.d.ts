import type { CustomRouteHandle } from '@/app/AppRouter/types'
import 'react-router'
import type { UIMatch } from 'react-router'

declare module 'react-router' {
  export function useMatches(): UIMatch<
    unknown,
    CustomRouteHandle | undefined
  >[]
}
