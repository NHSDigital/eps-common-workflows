# EPS Common Workflow - copilot instructions

## Overview
This contains common github workflows that are used by other EPS projects

## General
These rules should be followed for all workflows

*NEVER* use a version number in 3rd party actions or workflows - always use the git commit sha instead
*NEVER* use secrets: inherit in a workflow - always define what secrets are being passed through to another workflow
*NEVER* use an input to a workflow directly in a code execution block. Always define an environment variable and use that in the code execution block

All use of 3rd party actions or workflows outside of NHSDigital github org should be carefully evaluated before deciding to use them. Notice should be taken of
 - How often is the action or workflow updated. Avoid any workflows that have not been updated in over a year
 - Can the action or workflow be easily written locally with a few simple shell or github actions commands

All workflows that are designed to be called from another repo should have a `workflow_call` trigger. 
Workflows designed to be called from other repos should be documented in the README.md file
