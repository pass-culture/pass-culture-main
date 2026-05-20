/**
 * Parses a single `*.module.{scss,css,sass}` file and returns the set of
 * locally-declared classes together with disable-comment metadata.
 *
 * Two regexes recognize the upstream disable-comment syntax:
 *   /* check-unused-css-disable *\/             (entire file)
 *   /* check-unused-css-disable-next-line *\/   (next rule)
 *
 * The walker resolves SCSS `&-suffix` nesting against the parent rule so
 * `.parent { &-x { ... } }` declares `.parent-x`. Rules nested inside
 * `@keyframes` are ignored entirely (their selectors are percentage or
 * keyword tokens, not class names).
 */

import { readFile } from 'node:fs/promises'
import postcssScss from 'postcss-scss'
import selectorParser from 'postcss-selector-parser'

const SCSS_DISABLE_FILE_RE = /\/\*\s*check-unused-css-disable\s*\*\//
const SCSS_DISABLE_LINE_RE = /\/\*\s*check-unused-css-disable-next-line\s*\*\//

function isInsideKeyframes(rule) {
  let parent = rule.parent
  while (parent) {
    if (parent.type === 'atrule' && /keyframes/i.test(parent.name)) return true
    parent = parent.parent
  }
  return false
}

/**
 * Splits a comma-separated selector list, ignoring commas nested inside
 * parentheses (`:not(.a, .b)`) or brackets (`[attr="a,b"]`). Faster than
 * round-tripping through an AST when we only need the top-level split.
 */
function splitSelectorList(selector) {
  const parts = []
  let depth = 0
  let buffer = ''
  for (const char of selector) {
    if (char === '(' || char === '[') depth += 1
    else if (char === ')' || char === ']') depth -= 1
    if (char === ',' && depth === 0) {
      const trimmed = buffer.trim()
      if (trimmed) parts.push(trimmed)
      buffer = ''
    } else {
      buffer += char
    }
  }
  const trimmed = buffer.trim()
  if (trimmed) parts.push(trimmed)
  return parts
}

/**
 * Returns the set of CSS-module class names declared by a selector,
 * skipping classes that appear inside `:global(...)` (those are intentional
 * escapes from the CSS-module name space).
 */
function extractClassesFromSelector(selector) {
  const found = new Set()
  selectorParser((root) => {
    root.walkClasses((node) => {
      let parent = node.parent
      while (parent) {
        if (parent.type === 'pseudo' && parent.value === ':global') return
        parent = parent.parent
      }
      found.add(node.value)
    })
  }).processSync(selector)
  return found
}

function resolveRuleSelectors(rule, ancestorSelectors) {
  const ownSelectors = splitSelectorList(rule.selector)
  if (ancestorSelectors.length === 0) return ownSelectors
  const resolved = []
  for (const own of ownSelectors) {
    if (own.includes('&')) {
      for (const ancestor of ancestorSelectors) {
        resolved.push(own.replaceAll('&', ancestor))
      }
    } else {
      for (const ancestor of ancestorSelectors) {
        resolved.push(`${ancestor} ${own}`)
      }
    }
  }
  return resolved
}

function isFileDisabled(lines) {
  const head = (lines[0] ?? '').trim()
  return SCSS_DISABLE_FILE_RE.test(head) && !SCSS_DISABLE_LINE_RE.test(head)
}

function buildDisabledLineSet(lines) {
  const disabled = new Set()
  for (let index = 0; index < lines.length; index += 1) {
    if (SCSS_DISABLE_LINE_RE.test(lines[index])) {
      disabled.add(index + 2)
    }
  }
  return disabled
}

/**
 * Returns `{ filePath, declared, suppressedUnused, fileDisabled?, parseError? }`:
 *   - `declared`: Map<className, lineNumber> of every class declared in the file,
 *   - `suppressedUnused`: Set<className> the unused-check must skip
 *     (classes adjacent to a `/* check-unused-css-disable-next-line *\/`).
 */
export async function parseModuleFile(filePath) {
  const source = await readFile(filePath, 'utf8')
  const lines = source.split('\n')
  if (isFileDisabled(lines)) {
    return {
      filePath,
      declared: new Map(),
      suppressedUnused: new Set(),
      fileDisabled: true,
    }
  }
  const disabledLines = buildDisabledLineSet(lines)
  let root
  try {
    root = postcssScss.parse(source, { from: filePath })
  } catch (error) {
    return {
      filePath,
      declared: new Map(),
      suppressedUnused: new Set(),
      parseError: error,
    }
  }
  const declared = new Map()
  const suppressedUnused = new Set()

  function walk(node, ancestorSelectors) {
    if (node.type === 'rule') {
      if (isInsideKeyframes(node)) return
      const resolved = resolveRuleSelectors(node, ancestorSelectors)
      const ruleLine = node.source?.start?.line
      for (const selectorText of resolved) {
        for (const className of extractClassesFromSelector(selectorText)) {
          if (!declared.has(className)) {
            declared.set(className, ruleLine ?? 0)
          }
        }
      }
      if (ruleLine !== undefined && disabledLines.has(ruleLine)) {
        for (const selectorText of resolved) {
          for (const className of extractClassesFromSelector(selectorText)) {
            suppressedUnused.add(className)
          }
        }
      }
      if (node.nodes) {
        for (const child of node.nodes) walk(child, resolved)
      }
      return
    }
    if (node.type === 'atrule' && node.nodes) {
      for (const child of node.nodes) walk(child, ancestorSelectors)
    }
  }

  for (const child of root.nodes ?? []) walk(child, [])
  return { filePath, declared, suppressedUnused, fileDisabled: false }
}
