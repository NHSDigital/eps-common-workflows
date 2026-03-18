const {
    CloudFormationClient,
    ListExportsCommand
} = require("@aws-sdk/client-cloudformation")
const { LambdaClient, InvokeCommand } = require("@aws-sdk/client-lambda")

async function createAndTagJiraIssues(version, releasePrefix, jiraTickets) {
    try {
        const exportName = "release-notes:ReleaseCutLambdaName"
        const cloudFormationClient = new CloudFormationClient({})
        const lambdaClient = new LambdaClient({})

        let functionName
        let nextToken

        do {
            const exportsResponse = await cloudFormationClient.send(
                new ListExportsCommand({ NextToken: nextToken })
            )

            functionName = exportsResponse.Exports?.find(
                exportItem => exportItem.Name === exportName
            )?.Value

            nextToken = exportsResponse.NextToken
        } while (!functionName && nextToken)

        if (!functionName) {
            throw new Error(`Could not resolve CloudFormation export '${exportName}'`)
        }

        const payload = {
            releaseTag: version,
            releasePrefix,
            tickets: jiraTickets
        }

        await lambdaClient.send(
            new InvokeCommand({
                FunctionName: functionName,
                Payload: Buffer.from(JSON.stringify(payload))
            })
        )
    } catch (error) {
        console.error("Failed to create and tag Jira issues:", error)
    }

    return { success: true }
}

module.exports = {
    createAndTagJiraIssues,
    async success(pluginConfig, context) {
        const { nextRelease, commits } = context

        // use gitTag so it includes the prefix and suffix
        const version = nextRelease.gitTag

        // Extract Jira tickets from commit messages
        const jiraTickets = new Set()

        const jiraRegex = /([A-Z]+-\d+)/g

        for (const commit of commits) {
            const matches = commit.message.match(jiraRegex)
            if (matches) {
                matches.forEach(t => jiraTickets.add(t))
            }
        }

        const releasePrefix = pluginConfig?.releasePrefix
        if (!releasePrefix) {
            console.warn("JIRA_RELEASE_PREFIX is not set; invoking release-notes lambda with undefined releasePrefix.")
        }
        await createAndTagJiraIssues(version, releasePrefix, [...jiraTickets])
    }
}
