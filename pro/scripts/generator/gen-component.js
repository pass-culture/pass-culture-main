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
  'component'
)

export const generateComponent = async (componentName) => {
  try {
    const answers = await getAnswers()

    answers.scss = answers.scss === 'Yes' ? true : false
    answers.spec = answers.spec === 'Yes' ? true : false
    answers.storybook = answers.storybook === 'Yes' ? true : false

    const filesToGenerate = []
    filesToGenerate.push(`${componentName}.tsx`)
    if (answers.scss) filesToGenerate.push(`${componentName}.module.scss`)
    if (answers.spec) filesToGenerate.push(`${componentName}.spec.tsx`)
    if (answers.storybook) filesToGenerate.push(`${componentName}.stories.tsx`)

    console.log('\nThis will generate all these files:\n')
    console.log(
      getTreeFromAnswers(answers, filesToGenerate, componentName),
      '\n'
    )

    const confirm = await getConfirm()

    if (!confirm.ok) {
      return console.log('\nCancelled\n')
    }

    // Creates directory for the new component
    const dirName = path.join(answers.path, componentName)
    await fs.mkdir(dirName)

    const data = {
      cname: componentName,
      scss: { yes: answers.scss, no: !answers.scss },
      spec: { yes: answers.spec, no: !answers.spec },
      storybook: { yes: answers.storybook, no: !answers.storybook },
    }

    const parsedFiles = [
      parseAndGenerateFile('<% cname %>.tsx.mustache', data, dirName),
    ]
    if (answers.scss) {
      parsedFiles.push(
        parseAndGenerateFile('<% cname %>.module.scss.mustache', data, dirName)
      )
    }
    if (answers.spec) {
      parsedFiles.push(
        parseAndGenerateFile('<% cname %>.spec.tsx.mustache', data, dirName)
      )
    }
    if (answers.storybook) {
      parsedFiles.push(
        parseAndGenerateFile('<% cname %>.stories.tsx.mustache', data, dirName)
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
      name: 'scss',
      message: 'Generate SCSS module?',
      choices: ['Yes', 'No'],
    },
    {
      type: 'list',
      name: 'spec',
      message: 'Generate test file?',
      choices: ['Yes', 'No'],
    },
    {
      type: 'list',
      name: 'storybook',
      message: 'Generate storybook file?',
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

const getTreeFromAnswers = (answers, filesToGenerate, componentName) => {
  return (
    answers.path +
    printTree('', [
      (tab) =>
        componentName +
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
