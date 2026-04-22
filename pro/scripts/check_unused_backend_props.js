/**
 * Report unused Backend API types & props
 *
 * Strategy:
 * 1. Load the TS project via `ts-morph`, a static analysis library for TypeScript.
 * 2. Enumerate apiClient exported types (= Backend API queries & mutations types)
 * 3. Resolve each to its declaration, then use the TypeScript
 * language service (`findReferencesAsNodes`) to find consumer references.
 */

// @ts-check

import path from 'node:path'
import process from 'node:process'
import { Node, Project } from 'ts-morph'

/** @typedef { import('ts-morph').TypeAliasDeclaration | import('ts-morph').InterfaceDeclaration | import('ts-morph').EnumDeclaration} AnalyzableDeclaration */
/** @typedef {AnalyzableDeclaration | import('ts-morph').PropertySignature} ReferenceableNode */
/** @typedef {{ name: string; node: import('ts-morph').PropertySignature }} PropertyEntry */

const TSCONFIG_PATH = path.join(process.cwd(), 'tsconfig.json')
const BACKEND_API_TYPES_DIR_PATH = path.join(process.cwd(), 'src', 'apiClient')
const BACKEND_API_TYPES_INDEX_FILE_PATH = path.join(
  BACKEND_API_TYPES_DIR_PATH,
  'v1',
  'index.ts'
)

/**
 * @param {string} line
 * @returns {string}
 */
const toBoxLine = (line) => `┃ ${line.padEnd(76, ' ')} ┃`

/**
 * @param {import('ts-morph').SourceFile} sourceFile
 * @returns {boolean}
 */
const isInsideGeneratedClient = (sourceFile) =>
  sourceFile.getFilePath().startsWith(BACKEND_API_TYPES_DIR_PATH + path.sep)

/**
 * @param {string} absolutePath
 * @returns {string}
 */
const relativeFromRoot = (absolutePath) =>
  path.relative(process.cwd(), absolutePath)

/**
 * @param {ReferenceableNode} declaration
 * @returns {number}
 */
const countExternalReferences = (declaration) => {
  const nameNode = declaration.getNameNode()
  const declarationNode = Node.isReferenceFindable(nameNode)
    ? nameNode
    : declaration
  const referencedNodes = declarationNode.findReferencesAsNodes()
  let count = 0
  for (const node of referencedNodes) {
    if (node === declarationNode) {
      continue
    }
    if (isInsideGeneratedClient(node.getSourceFile())) {
      continue
    }

    count += 1
  }
  return count
}

/**
 * Enums are intentionally skipped here.
 *
 * @param {AnalyzableDeclaration} declaration
 * @returns {PropertyEntry[]}
 */
const collectPropertyDeclarations = (declaration) => {
  if (Node.isEnumDeclaration(declaration)) {
    return []
  }

  if (Node.isInterfaceDeclaration(declaration)) {
    return declaration.getProperties().map((property) => ({
      name: property.getName(),
      node: property,
    }))
  }

  const typeNode = declaration.getTypeNode()
  if (!typeNode || !Node.isTypeLiteral(typeNode)) {
    return []
  }

  return typeNode.getProperties().map((property) => ({
    name: property.getName(),
    node: property,
  }))
}

/**
 * @param {import('ts-morph').Node} declaration
 * @returns {declaration is AnalyzableDeclaration}
 */
const isAnalyzableDeclaration = (declaration) =>
  Node.isTypeAliasDeclaration(declaration) ||
  Node.isInterfaceDeclaration(declaration) ||
  Node.isEnumDeclaration(declaration)

/**
 * @param {import('ts-morph').Project} project
 * @returns {Array<{ exportedName: string; declaration: AnalyzableDeclaration }>}
 */
const collectBackendApiExportedTypes = (project) => {
  const backendApiTypesSourceFile = project.getSourceFile(
    BACKEND_API_TYPES_INDEX_FILE_PATH
  )
  if (!backendApiTypesSourceFile) {
    throw new Error(
      `Could not load Backend API types at ${relativeFromRoot(BACKEND_API_TYPES_INDEX_FILE_PATH)}.`
    )
  }

  /** @type {Array<{ exportedName: string; declaration: AnalyzableDeclaration }>} */
  const exportedTypes = []
  /** @type {Set<string>} */
  const checkedTypeKeys = new Set()

  for (const [
    exportedName,
    declarations,
  ] of backendApiTypesSourceFile.getExportedDeclarations()) {
    for (const declaration of declarations) {
      if (!isAnalyzableDeclaration(declaration)) {
        continue
      }
      if (!isInsideGeneratedClient(declaration.getSourceFile())) {
        continue
      }

      const key = `${declaration.getSourceFile().getFilePath()}::${declaration.getName()}`
      if (checkedTypeKeys.has(key)) {
        continue
      }

      checkedTypeKeys.add(key)
      exportedTypes.push({ exportedName, declaration })
    }
  }

  return exportedTypes
}

const run = () => {
  try {
    const startedAt = Date.now()
    console.info(
      `> Loading TypeScript project from ${relativeFromRoot(TSCONFIG_PATH)}...`
    )

    const project = new Project({
      tsConfigFilePath: TSCONFIG_PATH,
      skipAddingFilesFromTsConfig: false,
    })

    const exportedTypes = collectBackendApiExportedTypes(project)
    console.info(
      `> Inspecting ${exportedTypes.length} types exported by ${relativeFromRoot(BACKEND_API_TYPES_INDEX_FILE_PATH)}...`
    )

    const fullyUnusedTypes = []
    const partiallyUnusedTypes = []

    let inspectedTypeIndex = 0
    for (const { exportedName, declaration } of exportedTypes) {
      inspectedTypeIndex += 1

      process.stdout.write(`· ${inspectedTypeIndex}/${exportedTypes.length}\r`)

      const sourceFile = declaration.getSourceFile()
      const externalRefs = countExternalReferences(declaration)

      if (externalRefs === 0) {
        fullyUnusedTypes.push({
          name: exportedName,
          kind: declaration.getKindName(),
          file: relativeFromRoot(sourceFile.getFilePath()),
        })

        continue
      }

      const properties = collectPropertyDeclarations(declaration)
      const unusedProperties = []
      for (const property of properties) {
        const propertyRefs = countExternalReferences(property.node)
        if (propertyRefs === 0) {
          unusedProperties.push(property.name)
        }
      }

      if (unusedProperties.length > 0) {
        partiallyUnusedTypes.push({
          name: exportedName,
          file: relativeFromRoot(sourceFile.getFilePath()),
          props: unusedProperties,
        })
      }
    }

    const elapsedSeconds = ((Date.now() - startedAt) / 1000).toFixed(1)
    process.stdout.write(`${' '.repeat(60)}\r`)

    console.info()
    console.info(`┏ FULLY UNUSED TYPES ${'━'.repeat(58)}┓`)
    console.info(toBoxLine(''))
    if (fullyUnusedTypes.length === 0) {
      console.info(toBoxLine('✓ None'))
    } else {
      for (const entry of fullyUnusedTypes) {
        console.info(toBoxLine(`x ${entry.name} (${entry.kind})`))
      }
    }
    console.info(`┗${'━'.repeat(78)}┛`)

    console.info()
    console.info(`┏ PARTIALLY UNUSED TYPES ${'━'.repeat(54)}┓`)
    console.info(toBoxLine(''))
    if (partiallyUnusedTypes.length === 0) {
      console.info('┃ ✓ None')
    } else {
      for (const entry of partiallyUnusedTypes) {
        console.info(toBoxLine(`x ${entry.name}`))
        for (const propName of entry.props) {
          console.info(toBoxLine(`  - ${propName}`))
        }
      }
    }
    console.info(`┗${'━'.repeat(78)}┛`)

    const totalUnusedProps = partiallyUnusedTypes.reduce(
      (total, entry) => total + entry.props.length,
      0
    )

    console.info()
    console.info(`┏ SUMMARY ${'━'.repeat(69)}┓`)
    console.info(toBoxLine(''))
    console.info(toBoxLine(`Inspected types        : ${exportedTypes.length}`))
    console.info(
      toBoxLine(`Fully unused types     : ${fullyUnusedTypes.length}`)
    )
    console.info(
      toBoxLine(`Partially unused types : ${partiallyUnusedTypes.length}`)
    )
    console.info(toBoxLine(`Elapsed                : ${elapsedSeconds}s`))
    console.info(`┗${'━'.repeat(78)}┛`)

    const hasFindings = fullyUnusedTypes.length > 0 || totalUnusedProps > 0
    process.exitCode = hasFindings ? 1 : 0
  } catch (error) {
    console.error(error)
    // `2` because `1` represents normal linting failure (= there are some unused props)
    process.exit(2)
  }
}

run()
