function adoptCallSiteStack(error: unknown, callSite: Error): void {
  if (!(error instanceof Error)) {
    return
  }

  callSite.name = error.name
  callSite.message = error.message

  if (callSite.stack) {
    error.stack = callSite.stack
  }
}

type SdkOperation = (...args: never[]) => Promise<unknown>

/**
 * Wraps one operation so that its failures carry the stack of their caller.
 */
function recordCallSite<Operation extends SdkOperation>(
  operation: Operation
): Operation {
  const wrapped = async (...args: Parameters<Operation>) => {
    // Captured synchronously, before the operation is entered
    const callSite = new Error()

    try {
      return await operation(...args)
    } catch (error) {
      adoptCallSiteStack(error, callSite)
      throw error
    }
  }

  return wrapped as Operation
}

/**
 * Returns a copy of a generated SDK whose every operation records its call site.
 */
export function withCallSites<Sdk extends object>(sdk: Sdk): Sdk {
  const operations = Object.entries(sdk).map(([name, value]) => {
    const isOperation = typeof value === 'function'
    return [name, isOperation ? recordCallSite(value) : value] as const
  })

  // the cast restores the generated signatures
  return Object.fromEntries(operations) as Sdk
}
