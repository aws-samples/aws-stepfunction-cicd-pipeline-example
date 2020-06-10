# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json

"""
This class is a Data Structure that holds metadata about the pipeline execution
In particular it is useful for validating the input and output of the entire pipeline

"""
class PipelineExecutionMetadata():
    def __init__(
        self,
        executionarn: str,
        status: str,
        inputval: str,
        output: str,
        retries: str
    ):
        self.executionarn = executionarn
        self.status = status
        self.inputval = inputval
        self.output = output
        self.retries = retries
    
    def __repr__(self):
        response = {}
        response['executionarn'] = self.executionarn
        response['status'] = self.status
        response['inputval'] = self.inputval
        response['output'] = self.output
        response['retries'] = self.retries
        return json.dumps(response)
    
    def get_executionarn(self):
        return self.executionarn
    
    def get_status(self):
        return self.status
    
    def get_inputval(self):
        return self.inputval
    
    def get_output(self):
        return self.output
    
    def get_retries(self):
        return self.retries
