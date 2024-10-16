import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs/promises'

import inquirer from 'inquirer'
import inquirerFuzzyPath from 'inquirer-fuzzy-path'
import { printTree } from 'tree-dump'
import Mustache from 'mustache'

Mustache.tags = ['<%', '%>']

inquirer.registerPrompt('fuzzypath', inquirerFuzzyPath)

const SRC_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '../../src'
)

const TEMPLATES_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '_templates',
  'util'
)

export const generateUtil = async (utilName) => {
  try {
    const answers = await getAnswers()

    answers.spec = answers.spec === 'Yes' ? true : false

    const filesToGenerate = []
    filesToGenerate.push(`${utilName}.ts`)
    if (answers.spec) filesToGenerate.push(`${utilName}.spec.ts`)

    console.log('\nThis will generate all these files:\n')
    console.log(getTreeFromAnswers(answers, filesToGenerate), '\n')

    const confirm = await getConfirm()

    if (!confirm.ok) {
      return console.log('\nCancelled\n')
    }

    // Creates directory for the new component
    const dirName = path.join(answers.path)

    const data = {
      cname: utilName,
      spec: { yes: answers.spec, no: !answers.spec },
    }

    const parsedFiles = [
      parseAndGenerateFile('<% cname %>.ts.mustache', data, dirName),
    ]
    if (answers.spec) {
      parsedFiles.push(
        parseAndGenerateFile('<% cname %>.spec.ts.mustache', data, dirName)
      )
    }

    const result = await Promise.all(parsedFiles)

    console.log('\nSuccessfully generated files:\n')
    console.log(result.map(({ fullname }) => ` - ${fullname}`).join('\n'), '\n')
  } catch (err) {
    handleError(err)
  }
}

const getAnswers = async () => {
  return inquirer.prompt([
    {
      type: 'fuzzypath',
      name: 'path',
      excludePath: (nodePath) => nodePath.includes('node_modules'),
      itemType: 'directory',
      rootPath: SRC_PATH,
      message: 'Target directory?',
    },
    {
      type: 'list',
      name: 'spec',
      message: 'Generate test file?',
      choices: ['Yes', 'No'],
    },
  ])
}

const getConfirm = async () => {
  return inquirer.prompt([
    {
      type: 'confirm',
      name: 'ok',
      message: 'Is that ok?',
      default: true,
    },
  ])
}

const getTreeFromAnswers = (answers, filesToGenerate) => {
  return (
    answers.path +
    printTree('', [
      (tab) =>
        printTree(
          tab,
          filesToGenerate.map((f) => () => f)
        ),
    ])
  )
}

const parseAndGenerateFile = async (templateName, data, dirName) => {
  const fullname = path.join(
    dirName,
    Mustache.render(templateName.replace('.mustache', ''), data)
  )

  // Parse Mustache file
  const templateContent = await fs.readFile(
    path.join(TEMPLATES_PATH, templateName),
    'utf8'
  )
  const parsedContent = Mustache.render(templateContent, data)

  // Write file
  await fs.writeFile(fullname, parsedContent, 'utf8')

  return { fullname }
}

const handleError = (err) => {
  switch (err.name) {
    case 'ExitPromptError':
      console.log('\nUser Aborted!\n')
      break

    default:
      console.log('\nUnknown error:', err.message, '\n')
  }

  process.exit(0)
}
