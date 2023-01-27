<!--
title: 'AWS Python Example'
description: 'This template demonstrates how to deploy a Python function running on AWS Lambda using the traditional Serverless Framework.'
layout: Doc
framework: v3
platform: AWS
language: python
priority: 2
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->

# Python thumbnail generator

A generator that uses:

- Python
- Serverless
- AWS: S3, DynamoDB, Lambda and API Gateway

## How it works?

You just need to upload an image on a S3 bucket and it generates a thumbnail of it, with smaller dimensions and size. By the way, if you want to get thumbnails data it is simple, just request it on API Gateway endpoint.
