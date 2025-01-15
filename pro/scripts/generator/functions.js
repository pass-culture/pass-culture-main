import fs from 'node:fs/promises'
import path from 'node:path'

import inquirer from 'inquirer'
import inquirerFuzzyPath from 'inquirer-fuzzy-path'
import Mustache from 'mustache'
import { printTree } from 'tree-dump'

inquirer.registerPrompt('fuzzypath', inquirerFuzzyPath)

Mustache.tags = ['<%', '%>']

export const exitWithScriptError = (message) => {
  console.log(`\n❌ ${message}\n`)
  process.exit(1)
}

export const getConfig = async (templatePath) => {
  try {
    return (await import(path.join(templatePath, 'config.js'))).default
  } catch (err) {
    throw new Error(`Cannot find config file in ${templatePath}`)
  }
}

export const getAnswers = async (configFilesToGenerate, name = null) => {
  const inquirerQuestions = configFilesToGenerate
    .filter((file) => !!file.question && !!file.varName)
    .map((file) => ({
      type: 'list',
      name: file.varName,
      message: file.question,
      choices: ['Yes', 'No'],
    }))

  try {
    return await inquirer.prompt(
      [
        {
          type: 'fuzzypath',
          name: 'targetDirectory',
          excludePath: (nodePath) => nodePath.includes('node_modules'),
          itemType: 'directory',
          rootPath: './src',
          message: 'Target directory?',
        },
        name && {
          type: 'confirm',
          name: 'createNewDirectory',
          message: `Create sub-directory /${name}/ ?`,
          default: true,
        },
        ...inquirerQuestions,
      ].filter(Boolean)
    )
  } catch (err) {
    if (err.name === 'ExitPromptError') {
      throw new Error(`Operation aborted: User cancelled`)
    }
    throw new Error(`Could not get answers: ${err.message}`)
  }
}

export const getConfirm = async () => {
  try {
    return await inquirer.prompt([
      {
        type: 'confirm',
        name: 'ok',
        message: 'Is that ok?',
        default: true,
      },
    ])
  } catch (err) {
    if (err.name === 'ExitPromptError') {
      throw new Error(`Operation aborted: User cancelled`)
    }
    throw new Error(`Could not get answers: ${err.message}`)
  }
}

export const makeFilesTree = ({ baseRoot, newDirectoryName, fileNames }) => {
  const treeContent = newDirectoryName
    ? [
        (tab) =>
          newDirectoryName +
          printTree(
            tab,
            fileNames.map((f) => () => f)
          ),
      ]
    : fileNames.map((f) => () => f)

  return baseRoot + printTree('', treeContent)
}

export const createDirectory = async (targetDirectory) => {
  try {
    await fs.mkdir(targetDirectory)
  } catch (err) {
    if (err.code === 'EEXIST') {
      throw new Error(`Directory already exists: ${targetDirectory}`)
    }
    throw new Error(`Could not create directory: ${err.message}`)
  }
}

export const parseAndGenerateFile = async ({
  templateFileName,
  renderedFileName,
  data,
}) => {
  try {
    // Parse Mustache file
    const templateContent = await fs.readFile(templateFileName, 'utf8')
    const parsedContent = Mustache.render(templateContent, {
      ...data,
      toKebabCase,
    })

    // Write new file parsed
    await fs.writeFile(renderedFileName, parsedContent, 'utf8')
  } catch (err) {
    throw new Error(
      `Could not create file: ${renderedFileName} (${err.message})`
    )
  }
}

// Internal mustache templates :

function toKebabCase() {
  return (str, render) =>
    render(str)
      .match(
        /[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g
      )
      ?.map((x) => x.toLowerCase())
      .join('-')
}
