// eslint-disable-next-line @typescript-eslint/no-var-requires
const { readFileSync } = require("fs")

const commitTemplate = readFileSync("./releaseNotesTemplates/commit.hbs").toString()
const publish_package = process.env.PUBLISH_PACKAGE === "true"
const publish_subpackages = process.env.PUBLISH_SUBPACKAGES?.split(",").map(s => s.trim()).filter(s => s.length > 0) || []
const mainBranch = process.env.MAIN_BRANCH || "main"

module.exports = {
    branches: [
        {
            name: mainBranch
        }
    ],
    plugins: [
        [
            "@semantic-release/commit-analyzer",
            {
                preset: "eslint",
                releaseRules: [
                    {
                        tag: "Fix",
                        release: "patch"
                    },
                    {
                        tag: "Update",
                        release: "patch"
                    },
                    {
                        tag: "New",
                        release: "minor"
                    },
                    {
                        tag: "Breaking",
                        release: "major"
                    },
                    {
                        tag: "Docs",
                        release: "patch"
                    },
                    {
                        tag: "Build",
                        release: false
                    },
                    {
                        tag: "Upgrade",
                        release: "patch"
                    },
                    {
                        tag: "Chore",
                        release: "patch"
                    }
                ]
            }
        ],
        [
            "@semantic-release/release-notes-generator",
            {
                preset: "eslint",
                writerOpts: {
                    commitPartial: commitTemplate
                }
            }
        ],
        [
            "@semantic-release/changelog",
            {
                changelogFile: "CHANGELOG.md"
            }
        ],
        ...(publish_package ? ["@semantic-release/npm"] : []),
        ...publish_subpackages.map(subpackage => [
            "@semantic-release/npm",
            {
                pkgRoot: subpackage
            }
        ]),
        [
            "@semantic-release/github",
            {
                assets: [
                    {
                        path: "CHANGELOG.md",
                        label: "CHANGELOG.md"
                    },
                    ...(process.env.EXTRA_ASSET ? [
                        {
                            path: process.env.EXTRA_ASSET,
                            label: process.env.EXTRA_ASSET
                        }
                    ] : [])
                ],
                successComment: false,
                failComment: false,
                failTitle: false
            }
        ]
    ]
}
