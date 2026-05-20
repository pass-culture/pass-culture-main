/**
 * Parses a TS / TSX / JS / JSX file and returns the imports of CSS-module
 * files together with the static and dynamic accesses on each bound
 * identifier.
 *
 * The access scanner walks the file character by character to find
 * `<binding>.foo`, `<binding>['foo']`, `<binding>[\`foo\`]` (static) and
 * `<binding>[<expr>]` (dynamic) without using a regex with nested
 * alternation (avoids ReDoS-style worst cases on adversarial input).
 *
 * Strings are not tracked at the top level on purpose: French JSX text
 * such as `l'inscription` would otherwise hide every subsequent
 * `styles.x` reference. The accepted trade-off is a rare false-negative
 * when a literal string happens to contain a `binding.x` token — that
 * direction merely hides a real "unused" warning, which is strictly safer
 * than the opposite direction (silently swallowing valid usages).
 */

import { readFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

import { PROJECT_ROOT, SRC_ROOT } from './paths.js'

const IMPORT_RE =
  /import\s+(?:(\w+)|\*\s+as\s+(\w+))\s+from\s+['"]([^'"]+\.module\.(?:s?css|sass))['"]/g
const REQUIRE_RE =
  /(?:const|let|var)\s+(\w+)\s*=\s*require\(['"]([^'"]+\.module\.(?:s?css|sass))['"]\)/g
const TS_DISABLE_FILE_RE = /^\s*\/\/\s*check-unused-css-disable\s*$/m
const TS_DISABLE_LINE_RE =
  /(?:\/\/|\{?\s*\/\*)\s*check-unused-css-disable-next-line\s*\*?\/?\}?/

const CHAR_TAB = 9
const CHAR_NEWLINE = 10
const CHAR_CARRIAGE_RETURN = 13
const CHAR_SPACE = 32
const CHAR_DOUBLE_QUOTE = 34
const CHAR_DOLLAR = 36
const CHAR_SINGLE_QUOTE = 39
const CHAR_ASTERISK = 42
const CHAR_HYPHEN = 45
const CHAR_DOT = 46
const CHAR_FORWARD_SLASH = 47
const CHAR_LEFT_BRACKET = 91
const CHAR_BACKSLASH = 92
const CHAR_RIGHT_BRACKET = 93
const CHAR_UNDERSCORE = 95
const CHAR_BACKTICK = 96
const CHAR_LEFT_BRACE = 123

function isIdentStart(code) {
  return (
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122) ||
    code === CHAR_UNDERSCORE ||
    code === CHAR_DOLLAR
  )
}

function isIdentCont(code) {
  return (
    (code >= 48 && code <= 57) ||
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122) ||
    code === CHAR_UNDERSCORE ||
    code === CHAR_DOLLAR
  )
}

function isClassNameChar(code) {
  return (
    (code >= 48 && code <= 57) ||
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122) ||
    code === CHAR_UNDERSCORE ||
    code === CHAR_HYPHEN
  )
}

function isWhitespace(code) {
  return (
    code === CHAR_SPACE ||
    code === CHAR_TAB ||
    code === CHAR_NEWLINE ||
    code === CHAR_CARRIAGE_RETURN
  )
}

function buildLineStarts(source) {
  const starts = [0]
  for (let index = 0; index < source.length; index += 1) {
    if (source.charCodeAt(index) === CHAR_NEWLINE) starts.push(index + 1)
  }
  return starts
}

function lineFromOffset(lineStarts, offset) {
  let lo = 0
  let hi = lineStarts.length - 1
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1
    if (lineStarts[mid] <= offset) lo = mid
    else hi = mid - 1
  }
  return lo + 1
}

function resolveImport(specifier, importingFile) {
  if (specifier.startsWith('./') || specifier.startsWith('../')) {
    return resolve(dirname(importingFile), specifier)
  }
  if (specifier.startsWith('@/')) {
    return resolve(SRC_ROOT, specifier.slice(2))
  }
  if (specifier.startsWith('/')) {
    return resolve(PROJECT_ROOT, specifier.slice(1))
  }
  return resolve(SRC_ROOT, specifier)
}

function findImports(source, filePath) {
  const imports = []
  for (const match of source.matchAll(IMPORT_RE)) {
    const binding = match[1] ?? match[2]
    if (!binding) continue
    imports.push({
      binding,
      modulePath: resolveImport(match[3], filePath),
    })
  }
  for (const match of source.matchAll(REQUIRE_RE)) {
    imports.push({
      binding: match[1],
      modulePath: resolveImport(match[2], filePath),
    })
  }
  return imports
}

function buildAccesses(source, bindings) {
  const fileDisabled = TS_DISABLE_FILE_RE.test(source)
  const result = new Map()
  for (const binding of bindings) {
    result.set(binding, { static: [], dynamic: false })
  }
  if (fileDisabled || bindings.length === 0) {
    return { accesses: result, fileDisabled }
  }
  const lines = source.split('\n')
  const disabledLines = new Set()
  for (let index = 0; index < lines.length; index += 1) {
    if (TS_DISABLE_LINE_RE.test(lines[index])) disabledLines.add(index + 2)
  }
  const bindingSet = new Set(bindings)
  const lineStarts = buildLineStarts(source)
  const length = source.length
  let i = 0
  while (i < length) {
    const code = source.charCodeAt(i)
    if (
      code === CHAR_FORWARD_SLASH &&
      source.charCodeAt(i + 1) === CHAR_FORWARD_SLASH
    ) {
      while (i < length && source.charCodeAt(i) !== CHAR_NEWLINE) i += 1
      continue
    }
    if (
      code === CHAR_FORWARD_SLASH &&
      source.charCodeAt(i + 1) === CHAR_ASTERISK
    ) {
      i += 2
      while (i + 1 < length) {
        if (
          source.charCodeAt(i) === CHAR_ASTERISK &&
          source.charCodeAt(i + 1) === CHAR_FORWARD_SLASH
        ) {
          i += 2
          break
        }
        i += 1
      }
      continue
    }
    if (!isIdentStart(code)) {
      i += 1
      continue
    }
    if (i > 0) {
      const prev = source.charCodeAt(i - 1)
      if (prev === CHAR_DOT || isIdentCont(prev)) {
        i += 1
        while (i < length && isIdentCont(source.charCodeAt(i))) i += 1
        continue
      }
    }
    const start = i
    i += 1
    while (i < length && isIdentCont(source.charCodeAt(i))) i += 1
    const ident = source.slice(start, i)
    if (!bindingSet.has(ident)) continue
    const usage = result.get(ident)
    const line = lineFromOffset(lineStarts, start)
    const disabled = disabledLines.has(line)
    const next = source.charCodeAt(i)
    if (next === CHAR_DOT) {
      const keyStart = i + 1
      let keyEnd = keyStart
      if (
        keyEnd < length &&
        source.charCodeAt(keyEnd) === CHAR_HYPHEN &&
        isClassNameChar(source.charCodeAt(keyEnd + 1))
      ) {
        keyEnd += 1
      }
      while (keyEnd < length && isClassNameChar(source.charCodeAt(keyEnd))) {
        keyEnd += 1
      }
      if (keyEnd > keyStart) {
        usage.static.push({
          name: source.slice(keyStart, keyEnd),
          line,
          disabled,
        })
      }
      i = keyEnd
      continue
    }
    if (next !== CHAR_LEFT_BRACKET) continue
    i += 1
    while (i < length && isWhitespace(source.charCodeAt(i))) i += 1
    const first = source.charCodeAt(i)
    if (first === CHAR_SINGLE_QUOTE || first === CHAR_DOUBLE_QUOTE) {
      const quote = first
      const keyStart = i + 1
      i = keyStart
      while (i < length) {
        const ch = source.charCodeAt(i)
        if (ch === CHAR_BACKSLASH && i + 1 < length) {
          i += 2
          continue
        }
        if (ch === quote) break
        i += 1
      }
      usage.static.push({ name: source.slice(keyStart, i), line, disabled })
      while (i < length && source.charCodeAt(i) !== CHAR_RIGHT_BRACKET) i += 1
      if (i < length) i += 1
      continue
    }
    if (first === CHAR_BACKTICK) {
      const keyStart = i + 1
      let hasInterpolation = false
      i = keyStart
      while (i < length) {
        const ch = source.charCodeAt(i)
        if (ch === CHAR_BACKSLASH && i + 1 < length) {
          i += 2
          continue
        }
        if (ch === CHAR_BACKTICK) break
        if (
          ch === CHAR_DOLLAR &&
          source.charCodeAt(i + 1) === CHAR_LEFT_BRACE
        ) {
          hasInterpolation = true
          break
        }
        i += 1
      }
      if (
        !hasInterpolation &&
        i < length &&
        source.charCodeAt(i) === CHAR_BACKTICK
      ) {
        usage.static.push({
          name: source.slice(keyStart, i),
          line,
          disabled,
        })
        i += 1
        while (i < length && source.charCodeAt(i) !== CHAR_RIGHT_BRACKET) {
          i += 1
        }
        if (i < length) i += 1
        continue
      }
      if (!disabled) usage.dynamic = true
      let depth = 1
      while (i < length && depth > 0) {
        const ch = source.charCodeAt(i)
        if (ch === CHAR_LEFT_BRACKET) depth += 1
        else if (ch === CHAR_RIGHT_BRACKET) depth -= 1
        i += 1
      }
      continue
    }
    if (!disabled) usage.dynamic = true
    let depth = 1
    while (i < length && depth > 0) {
      const ch = source.charCodeAt(i)
      if (ch === CHAR_LEFT_BRACKET) depth += 1
      else if (ch === CHAR_RIGHT_BRACKET) depth -= 1
      i += 1
    }
  }
  return { accesses: result, fileDisabled }
}

/**
 * Returns `{ filePath, imports, accesses, fileDisabled }` for a single source
 * file. `accesses` is a `Map<binding, { static: StaticRef[], dynamic: boolean }>`
 * where each `StaticRef` is `{ name, line, disabled }`.
 */
export async function parseSourceFile(filePath) {
  const source = await readFile(filePath, 'utf8')
  const imports = findImports(source, filePath)
  if (imports.length === 0) {
    return { filePath, imports: [], accesses: new Map(), fileDisabled: false }
  }
  const bindings = imports.map((entry) => entry.binding)
  const { accesses, fileDisabled } = buildAccesses(source, bindings)
  return { filePath, imports, accesses, fileDisabled }
}
