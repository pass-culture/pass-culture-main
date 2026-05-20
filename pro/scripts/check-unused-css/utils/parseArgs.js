/**
 * Parses CLI arguments into a `{ paths, excludes }` shape via Node's
 * built-in `util.parseArgs`.
 *
 * Accepts:
 *   - positional paths (defaults to `["src"]` when none are given),
 *   - `--exclude <glob>` / `-e <glob>` / `--exclude=<glob>` (repeatable),
 *   - `--help` / `-h` (prints usage and exits with code 0).
 */

import { parseArgs as nodeParseArgs } from 'node:util'

const USAGE = [
  'Usage: check-unused-css [<path>] [--exclude <glob>...]',
  'Default path is src/. Excludes accept glob patterns relative to <path>.',
].join('\n')

export function parseArgs(argv) {
  const { values, positionals } = nodeParseArgs({
    args: argv,
    options: {
      exclude: { type: 'string', short: 'e', multiple: true, default: [] },
      help: { type: 'boolean', short: 'h' },
    },
    allowPositionals: true,
  })

  if (values.help) {
    console.info(USAGE)
    process.exit(0)
  }

  return {
    paths: positionals.length > 0 ? positionals : ['src'],
    excludes: values.exclude,
  }
}
