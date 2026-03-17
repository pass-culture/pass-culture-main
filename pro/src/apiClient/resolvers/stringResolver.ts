/**
 * Custom hey-api string resolver that reads `x-error-messages` from the
 * OpenAPI schema and injects them as Zod error options.
 *
 * Pipeline: Pydantic `json_schema_extra={"x-error-messages": {...}}`
 *   -> OpenAPI `x-error-messages` extension on string properties
 *   -> This resolver reads those messages and produces e.g.
 *      `z.string().max(255, { error: "Title cannot exceed 255 characters" })`
 */

type ErrorMessages = Record<string, string>

interface StringResolverSchema {
  readonly minLength?: number
  readonly maxLength?: number
  readonly pattern?: string
  readonly 'x-error-messages'?: ErrorMessages
  readonly [key: `x-${string}`]: unknown
}

interface DslChain {
  attr(name: string): { call(...args: unknown[]): DslChain }
}

interface DslBuilder {
  object(): { prop(key: string, value: unknown): unknown }
  literal(value: string | number | boolean | null): unknown
  regexp(pattern: string, flags?: string): unknown
}

interface StringResolverContext {
  readonly $: DslBuilder
  readonly schema: StringResolverSchema
  readonly chain: { current: DslChain }
  readonly nodes: {
    base(context: StringResolverContext): DslChain
    const(context: StringResolverContext): DslChain | undefined
    format(context: StringResolverContext): DslChain | undefined
    length(context: StringResolverContext): DslChain | undefined
    maxLength(context: StringResolverContext): DslChain | undefined
    minLength(context: StringResolverContext): DslChain | undefined
    pattern(context: StringResolverContext): DslChain | undefined
  }
}

export function stringResolverWithErrorMessages(
  context: StringResolverContext
): DslChain | undefined {
  const errorMessages = context.schema['x-error-messages']

  if (!errorMessages) {
    return undefined
  }

  const constNode = context.nodes.const(context)
  if (constNode) {
    context.chain.current = constNode
    return context.chain.current
  }

  const baseNode = context.nodes.base(context)
  if (baseNode) {
    context.chain.current = baseNode
  }
  const formatNode = context.nodes.format(context)
  if (formatNode) {
    context.chain.current = formatNode
  }

  const { $ } = context

  const lengthNode = context.nodes.length(context)
  if (lengthNode) {
    context.chain.current = lengthNode
  } else {
    if (context.schema.minLength !== undefined) {
      const minArgs: unknown[] = [$.literal(context.schema.minLength)]
      if (errorMessages.min_length) {
        minArgs.push(
          $.object().prop('error', $.literal(errorMessages.min_length))
        )
      }
      context.chain.current = context.chain.current.attr('min').call(...minArgs)
    }

    if (context.schema.maxLength !== undefined) {
      const maxArgs: unknown[] = [$.literal(context.schema.maxLength)]
      if (errorMessages.max_length) {
        maxArgs.push(
          $.object().prop('error', $.literal(errorMessages.max_length))
        )
      }
      context.chain.current = context.chain.current.attr('max').call(...maxArgs)
    }
  }

  if (context.schema.pattern) {
    const patternArgs: unknown[] = [$.regexp(context.schema.pattern)]
    if (errorMessages.pattern) {
      patternArgs.push(
        $.object().prop('error', $.literal(errorMessages.pattern))
      )
    }
    context.chain.current = context.chain.current
      .attr('regex')
      .call(...patternArgs)
  }

  return context.chain.current
}
